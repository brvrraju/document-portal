import sys
import os
import time
from typing import Dict, List, Any
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from src.utils.logger import get_logger
from src.utils.exception import CustomException
from src.utils.aws_utils import get_dynamodb_resource
from boto3.dynamodb.conditions import Key

logger = get_logger("session_utils")

# Global session store for sharing history locally in memory during active turn
_session_store: Dict[str, ChatMessageHistory] = {}

class DynamoDBBackedHistory(ChatMessageHistory):
    def __init__(self, session_id: str):
        super().__init__()
        self.session_id = session_id
        self.table_name = os.getenv("DYNAMODB_TABLE_CHAT", "DocumentChatHistory")
        self.dynamodb = get_dynamodb_resource()
        self._load_from_db()

    def _load_from_db(self):
        try:
            table = self.dynamodb.Table(self.table_name)
            response = table.query(
                KeyConditionExpression=Key('session_id').eq(self.session_id)
            )
            items = response.get('Items', [])
            items.sort(key=lambda x: x.get('timestamp', 0))
            
            for item in items:
                msg_type = item.get('type')
                content = item.get('content', '')
                if msg_type == 'human':
                    super().add_user_message(content)
                elif msg_type == 'ai':
                    super().add_ai_message(content)
                elif msg_type == 'system':
                    super().add_message(SystemMessage(content=content))
        except Exception as e:
            logger.error(f"Failed to load history from DynamoDB: {e}")

    def add_message(self, message: BaseMessage) -> None:
        super().add_message(message)
        try:
            table = self.dynamodb.Table(self.table_name)
            item = {
                'session_id': self.session_id,
                'timestamp': int(time.time() * 1000),
                'type': message.type,
                'content': message.content
            }
            table.put_item(Item=item)
        except Exception as e:
            logger.error(f"Failed to save message to DynamoDB: {e}")

def get_session_history(session_id: str) -> ChatMessageHistory:
    """
    Retrieve or create a chat message history for a given session ID.
    This provides conversational memory backed by DynamoDB (if configured).
    """
    try:
        if session_id not in _session_store:
            table_name = os.getenv("DYNAMODB_TABLE_CHAT")
            if table_name:
                logger.info(f"Creating DynamoDB session history for session: {session_id}")
                _session_store[session_id] = DynamoDBBackedHistory(session_id)
            else:
                logger.info(f"DYNAMODB_TABLE_CHAT not set. Using local in-memory history for session: {session_id}")
                _session_store[session_id] = ChatMessageHistory()
        return _session_store[session_id]
    except Exception as e:
        raise CustomException(e, sys)

def get_pruned_messages(session_id: str, max_messages: int = 10) -> List[BaseMessage]:
    """
    Returns a pruned list of messages from the session history,
    keeping only the most recent N messages to avoid context limits.
    """
    try:
        history = get_session_history(session_id)
        messages = history.messages
        if len(messages) > max_messages:
            logger.info(f"Pruning session history for {session_id} from {len(messages)} to {max_messages} messages.")
            # Keep the last N messages
            pruned = messages[-max_messages:]
            return pruned
        return messages
    except Exception as e:
        raise CustomException(e, sys)
