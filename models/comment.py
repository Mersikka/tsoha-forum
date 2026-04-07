from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(init=False)
class ChildComment:
    id: int
    body: str
    user_id: int
    thread_id: int
    parent_comment_id: int | None
    created_at: str
    created_at_local: str
    username: str
    
    def __init__(
                 self,
                 id: int,
                 body: str,
                 user_id: int,
                 thread_id: int,
                 parent_comment_id: int | None,
                 created_at: str,
                 username: str,
             ):
        self.id = id
        self.body = body
        self.user_id = user_id
        self.thread_id = thread_id
        self.parent_comment_id = parent_comment_id
        self.created_at = created_at
        local_time = datetime.now().astimezone()
        utc_offset = local_time.utcoffset()
        created_time = datetime.strptime(
            created_at, r"%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)
        if utc_offset:
            created_time = created_time + utc_offset
        self.created_at_local = created_time.strftime(r"%Y-%m-%d %H:%M:%S")
        self.username = username



@dataclass
class ParentComment(ChildComment):
    children: list[ChildComment]
