# 所有会话的共享存储
sessions_store = {}      # session_id -> {name, created_at}
messages_store = {}      # session_id -> [{role, content}, ...]