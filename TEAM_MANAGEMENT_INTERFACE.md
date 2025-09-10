# Team Management Interface for aicache

## Overview
This document describes the design for a team management interface for aicache, enabling collaborative development and shared caching experiences.

## Key Features
1. **Team Creation and Management**: Create and manage development teams
2. **User Management**: Add/remove team members and manage roles
3. **Shared Cache Entries**: Share cache entries across team members
4. **Real-time Collaboration**: Live presence and activity tracking
5. **Permission System**: Granular access control for team resources
6. **Activity Feed**: Team-wide activity and notifications
7. **Performance Analytics**: Team performance and productivity metrics

## Architecture Components

### 1. Team Management Core
```
┌─────────────────────────────────────────────────────────┐
│                 Team Management System                  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Team Controller                        │ │
│  │  - Handle team creation/deletion                    │ │
│  │  - Manage team settings                             │ │
│  │  - Coordinate team operations                      │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              User Management                        │ │
│  │  - Add/remove team members                          │ │
│  │  - Manage user roles and permissions               │ │
│  │  - Handle invitations and approvals                 │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 2. Collaboration Services
```
┌─────────────────────────────────────────────────────────┐
│                 Collaboration Services                  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Presence Service                       │ │
│  │  - Track user online/offline status                 │ │
│  │  - Monitor user activity                            │ │
│  │  - Broadcast presence updates                       │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Cache Sharing Service                 │ │
│  │  - Manage shared cache entries                      │ │
│  │  - Handle cache entry permissions                  │ │
│  │  - Sync shared entries across team members         │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Notification Service                  │ │
│  │  - Send real-time notifications                    │ │
│  │  - Handle alert routing                             │ │
│  │  - Manage notification preferences                  │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 3. Analytics and Reporting
```
┌─────────────────────────────────────────────────────────┐
│               Analytics and Reporting                  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Team Analytics                         │ │
│  │  - Calculate team performance metrics               │ │
│  │  - Track productivity trends                        │ │
│  │  │  - Generate team reports                        │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Activity Feed                          │ │
│  │  - Aggregate team activities                        │ │
│  │  - Generate activity summaries                     │ │
│  │  - Provide activity filtering                        │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Key Modules

### 1. Team Controller (`team_controller.py`)
- Handle team lifecycle operations
- Manage team settings and configurations
- Coordinate team-wide operations

### 2. User Manager (`user_manager.py`)
- Manage team membership
- Handle user roles and permissions
- Process invitations and approvals

### 3. Presence Tracker (`presence_tracker.py`)
- Track user online status
- Monitor user activity
- Broadcast presence updates

### 4. Cache Sharer (`cache_sharer.py`)
- Manage shared cache entries
- Handle sharing permissions
- Sync shared entries

### 5. Notification Service (`notification_service.py`)
- Send real-time notifications
- Route alerts to team members
- Manage notification preferences

### 6. Team Analytics (`team_analytics.py`)
- Calculate team performance metrics
- Track productivity trends
- Generate team reports

### 7. Activity Feed (`activity_feed.py`)
- Aggregate team activities
- Generate activity summaries
- Provide activity filtering

## Integration Points

### 1. User Authentication
- **OAuth Integration**: GitHub, GitLab, Google
- **LDAP Integration**: Enterprise authentication
- **SAML Integration**: Single sign-on
- **JWT Tokens**: Secure session management

### 2. Real-time Communication
- **WebSocket Server**: Real-time updates
- **Message Broker**: Event distribution
- **Pub/Sub System**: Broadcast messaging
- **Streaming API**: Live data feeds

### 3. Cache System Integration
- **Cache API**: Access to shared cache entries
- **Event Streams**: Cache usage events
- **Performance Metrics**: Cache performance data
- **Usage Analytics**: Cache usage patterns

### 4. Notification Channels
- **Email**: Email notifications
- **Slack**: Slack integration
- **Discord**: Discord notifications
- **SMS**: Text message alerts
- **Mobile Push**: Push notifications

### 5. Analytics Platforms
- **Google Analytics**: Web analytics
- **Mixpanel**: User behavior analytics
- **Amplitude**: Product analytics
- **Custom Dashboards**: Internal analytics

## Data Flow

```
1. User Action → 2. Team Controller → 3. Service Processing → 4. Real-time Broadcast → 5. UI Update

┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐    ┌──────────┐
│ User Action  │ →  │ Team Controller  │ →  │ Service Processing│ →  │ Real-time Broadcast│ →  │ UI Update│
└──────────────┘    └──────────────────┘    └─────────────────┘    └──────────────────┘    └──────────┘
                              ↓                    ↓                    ↓                    ↓
                    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐    ┌──────────┐
                    │ User Management  │    │ Cache Operations│    │ Notification     │    │ Rendering│
                    └──────────────────┘    └─────────────────┘    └──────────────────┘    └──────────┘
```

## Security Considerations
- Role-based access control (RBAC)
- End-to-end encryption for communications
- Data encryption at rest
- Secure invitation and approval workflows
- Audit logging for compliance
- Two-factor authentication (2FA)

## Performance Optimization
- Caching for frequently accessed team data
- Database indexing for fast queries
- Connection pooling for database access
- Asynchronous processing for heavy operations
- Load balancing for high availability

## Development Setup
1. Install required dependencies
2. Set up authentication providers
3. Configure real-time communication services
4. Set up database connections
5. Configure notification channels

## Testing Strategy
- Unit tests for individual components
- Integration tests for service interactions
- Real-time communication tests
- Security tests for authentication
- Performance benchmarks for scalability

## Deployment
- Containerized deployment with Docker
- Orchestration with Kubernetes
- CI/CD pipeline for automated deployments
- Monitoring and alerting setup
- Backup and disaster recovery

## System Architecture

```
aicache-team-management/
├── src/
│   ├── controllers/                 # API controllers
│   │   ├── team_controller.py      # Team management
│   │   ├── user_controller.py       # User management
│   │   └── activity_controller.py   # Activity management
│   ├── services/                    # Business logic services
│   │   ├── team_service.py          # Team operations
│   │   ├── user_service.py          # User operations
│   │   ├── presence_service.py       # Presence tracking
│   │   ├── cache_sharing_service.py  # Cache sharing
│   │   ├── notification_service.py   # Notifications
│   │   ├── analytics_service.py      # Team analytics
│   │   └── activity_service.py      # Activity feed
│   ├── models/                      # Data models
│   │   ├── team.py                  # Team model
│   │   ├── user.py                  # User model
│   │   ├── membership.py            # Team membership
│   │   ├── role.py                  # Role model
│   │   ├── permission.py            # Permission model
│   │   ├── activity.py              # Activity model
│   │   └── notification.py          # Notification model
│   ├── realtime/                    # Real-time services
│   │   ├── websocket_server.py     # WebSocket server
│   │   ├── presence_tracker.py      # Presence tracking
│   │   └── event_publisher.py       # Event broadcasting
│   ├── utils/                      # Utility functions
│   │   ├── auth_utils.py           # Authentication utilities
│   │   ├── email_utils.py           # Email utilities
│   │   ├── config.py                # Configuration
│   │   └── logger.py                # Logging
│   └── main.py                      # Application entry point
├── tests/                           # Test files
│   ├── unit/
│   ├── integration/
│   └── performance/
├── migrations/                      # Database migrations
├── docs/                            # Documentation
├── requirements.txt                 # Python dependencies
├── docker-compose.yml               # Development setup
└── README.md                        # Project documentation
```

## Python Dependencies (`requirements.txt`)

```txt
fastapi==0.85.0
uvicorn==0.18.0
sqlalchemy==1.4.0
aiosqlite==0.17.0
psycopg2==2.9.0
redis==4.3.0
python-socketio==5.7.0
python-jose==3.3.0
passlib==1.7.0
bcrypt==4.0.0
pydantic==1.10.0
celery==5.2.0
requests==2.28.0
pandas==1.5.0
numpy==1.23.0
email-validator==1.3.0
sendgrid==6.9.0
slack-sdk==3.19.0
```

## Main Application Module (`src/main.py`)

```python
"""
Main application module for aicache team management
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .controllers.team_controller import router as team_router
from .controllers.user_controller import router as user_router
from .controllers.activity_controller import router as activity_router
from .realtime.websocket_server import sio
from .utils.config import get_config
from .utils.logger import get_logger

config = get_config()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Initializing aicache team management")
    
    # Initialize components
    # TODO: Initialize database connections
    # TODO: Initialize real-time services
    # TODO: Initialize notification services
    
    logger.info("aicache team management initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down aicache team management")

app = FastAPI(
    title="aicache Team Management API",
    description="Team collaboration and management for aicache",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get('ALLOWED_ORIGINS', ['*']),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(team_router, prefix="/api/teams", tags=["teams"])
app.include_router(user_router, prefix="/api/users", tags=["users"])
app.include_router(activity_router, prefix="/api/activity", tags=["activity"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": __import__('time').time(),
        "service": "aicache-team-management"
    }

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=config.get('HOST', '0.0.0.0'),
        port=config.get('PORT', 8000),
        reload=config.get('DEBUG', False)
    )
```

## Team Controller (`src/controllers/team_controller.py`)

```python
"""
Team controller for aicache team management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel

from ..services.team_service import TeamService
from ..utils.auth_utils import get_current_user

router = APIRouter()
team_service = TeamService()

class TeamCreateRequest(BaseModel):
    """Request model for creating a team"""
    name: str
    description: str = ""
    visibility: str = "private"  # private, public

class TeamUpdateRequest(BaseModel):
    """Request model for updating a team"""
    name: str = None
    description: str = None
    visibility: str = None

class TeamResponse(BaseModel):
    """Response model for team data"""
    id: str
    name: str
    description: str
    visibility: str
    created_at: str
    updated_at: str
    member_count: int

@router.post("/", response_model=TeamResponse)
async def create_team(
    request: TeamCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new team"""
    try:
        team = await team_service.create_team(
            name=request.name,
            description=request.description,
            visibility=request.visibility,
            creator_id=current_user['id']
        )
        return team
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get team information"""
    try:
        team = await team_service.get_team(team_id, current_user['id'])
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        return team
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    request: TeamUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update team information"""
    try:
        team = await team_service.update_team(
            team_id=team_id,
            user_id=current_user['id'],
            name=request.name,
            description=request.description,
            visibility=request.visibility
        )
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        return team
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{team_id}")
async def delete_team(
    team_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a team"""
    try:
        success = await team_service.delete_team(team_id, current_user['id'])
        if not success:
            raise HTTPException(status_code=404, detail="Team not found")
        return {"message": "Team deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TeamResponse])
async def list_teams(
    current_user: dict = Depends(get_current_user)
):
    """List teams for current user"""
    try:
        teams = await team_service.list_teams(current_user['id'])
        return teams
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## User Manager (`src/services/user_service.py`)

```python
"""
User service for aicache team management
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

from ..models.user import User
from ..models.membership import Membership
from ..utils.logger import get_logger

logger = get_logger(__name__)

class UserService:
    """Manage user operations for teams"""
    
    def __init__(self):
        self.users = {}  # In-memory storage for demo
        self.memberships = {}  # In-memory storage for demo
        
    async def add_user_to_team(
        self,
        user_id: str,
        team_id: str,
        role: str = "member",
        invited_by: str = None
    ) -> Dict[str, Any]:
        """Add user to team"""
        try:
            # Create membership record
            membership = {
                'id': f"membership_{len(self.memberships) + 1}",
                'user_id': user_id,
                'team_id': team_id,
                'role': role,
                'invited_by': invited_by,
                'joined_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            self.memberships[membership['id']] = membership
            logger.info(f"User {user_id} added to team {team_id} with role {role}")
            
            return membership
            
        except Exception as e:
            logger.error(f"Error adding user to team: {e}")
            raise
            
    async def remove_user_from_team(
        self,
        user_id: str,
        team_id: str
    ) -> bool:
        """Remove user from team"""
        try:
            # Find membership
            membership_id = None
            for mid, membership in self.memberships.items():
                if membership['user_id'] == user_id and membership['team_id'] == team_id:
                    membership_id = mid
                    break
                    
            if membership_id:
                del self.memberships[membership_id]
                logger.info(f"User {user_id} removed from team {team_id}")
                return True
                
            logger.warning(f"Membership not found for user {user_id} in team {team_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error removing user from team: {e}")
            raise
            
    async def get_team_members(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all members of a team"""
        try:
            members = []
            for membership in self.memberships.values():
                if membership['team_id'] == team_id and membership['status'] == 'active':
                    # Get user info
                    user_info = self.users.get(membership['user_id'], {
                        'id': membership['user_id'],
                        'username': f"user_{membership['user_id']}",
                        'email': f"user_{membership['user_id']}@example.com"
                    })
                    
                    members.append({
                        'user': user_info,
                        'role': membership['role'],
                        'joined_at': membership['joined_at']
                    })
                    
            return members
            
        except Exception as e:
            logger.error(f"Error getting team members: {e}")
            raise
            
    async def update_user_role(
        self,
        user_id: str,
        team_id: str,
        new_role: str
    ) -> bool:
        """Update user role in team"""
        try:
            # Find membership
            membership_id = None
            for mid, membership in self.memberships.items():
                if membership['user_id'] == user_id and membership['team_id'] == team_id:
                    membership_id = mid
                    break
                    
            if membership_id:
                self.memberships[membership_id]['role'] = new_role
                logger.info(f"User {user_id} role updated to {new_role} in team {team_id}")
                return True
                
            logger.warning(f"Membership not found for user {user_id} in team {team_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            raise
            
    async def invite_user(
        self,
        email: str,
        team_id: str,
        invited_by: str,
        role: str = "member"
    ) -> Dict[str, Any]:
        """Invite user to team"""
        try:
            # Create invitation record
            invitation = {
                'id': f"invite_{len(self.memberships) + 1}",
                'email': email,
                'team_id': team_id,
                'invited_by': invited_by,
                'role': role,
                'invited_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            # In a real implementation, this would send an email
            logger.info(f"Invitation sent to {email} for team {team_id}")
            
            return invitation
            
        except Exception as e:
            logger.error(f"Error inviting user: {e}")
            raise
```

## Presence Tracker (`src/realtime/presence_tracker.py`)

```python
"""
Presence tracker for aicache team management
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import json

from ..utils.logger import get_logger

logger = get_logger(__name__)

class PresenceTracker:
    """Track user presence and activity"""
    
    def __init__(self):
        self.presence_data = {}  # user_id -> presence info
        self.team_presence = {}  # team_id -> [user_ids]
        self.listeners = []  # presence change listeners
        
    async def update_presence(
        self,
        user_id: str,
        team_id: str,
        status: str,
        activity: str = None
    ):
        """Update user presence"""
        try:
            now = datetime.now().isoformat()
            
            # Update presence data
            self.presence_data[user_id] = {
                'user_id': user_id,
                'team_id': team_id,
                'status': status,
                'activity': activity,
                'last_seen': now,
                'updated_at': now
            }
            
            # Update team presence
            if team_id not in self.team_presence:
                self.team_presence[team_id] = set()
            self.team_presence[team_id].add(user_id)
            
            # Notify listeners
            await self._notify_presence_change(user_id, {
                'status': status,
                'activity': activity,
                'team_id': team_id
            })
            
            logger.debug(f"Presence updated for user {user_id}: {status}")
            
        except Exception as e:
            logger.error(f"Error updating presence: {e}")
            raise
            
    async def get_team_presence(self, team_id: str) -> List[Dict[str, Any]]:
        """Get presence information for team members"""
        try:
            if team_id not in self.team_presence:
                return []
                
            present_users = []
            now = datetime.now()
            
            for user_id in self.team_presence[team_id]:
                if user_id in self.presence_data:
                    presence_info = self.presence_data[user_id].copy()
                    
                    # Calculate time since last seen
                    last_seen_str = presence_info['last_seen']
                    last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                    time_since_seen = (now - last_seen).total_seconds()
                    
                    # Mark as offline if not seen for 5 minutes
                    if time_since_seen > 300:  # 5 minutes
                        presence_info['status'] = 'offline'
                        
                    present_users.append(presence_info)
                    
            return present_users
            
        except Exception as e:
            logger.error(f"Error getting team presence: {e}")
            raise
            
    async def get_user_presence(self, user_id: str) -> Dict[str, Any]:
        """Get presence information for a specific user"""
        try:
            return self.presence_data.get(user_id, {
                'user_id': user_id,
                'status': 'offline',
                'activity': None,
                'last_seen': None
            })
            
        except Exception as e:
            logger.error(f"Error getting user presence: {e}")
            raise
            
    async def add_presence_listener(self, listener):
        """Add a presence change listener"""
        self.listeners.append(listener)
        logger.debug("Presence listener added")
        
    async def remove_presence_listener(self, listener):
        """Remove a presence change listener"""
        if listener in self.listeners:
            self.listeners.remove(listener)
            logger.debug("Presence listener removed")
            
    async def _notify_presence_change(self, user_id: str, change_data: Dict[str, Any]):
        """Notify listeners of presence change"""
        for listener in self.listeners:
            try:
                await listener(user_id, change_data)
            except Exception as e:
                logger.error(f"Error notifying presence listener: {e}")
                
    async def cleanup_inactive_users(self):
        """Clean up presence data for inactive users"""
        try:
            now = datetime.now()
            inactive_users = []
            
            for user_id, presence_info in self.presence_data.items():
                last_seen_str = presence_info['last_seen']
                last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                time_since_seen = (now - last_seen).total_seconds()
                
                # Remove if not seen for 24 hours
                if time_since_seen > 86400:  # 24 hours
                    inactive_users.append(user_id)
                    
            # Clean up inactive users
            for user_id in inactive_users:
                del self.presence_data[user_id]
                logger.info(f"Cleaned up presence data for inactive user {user_id}")
                
        except Exception as e:
            logger.error(f"Error cleaning up inactive users: {e}")
```

## Cache Sharer (`src/services/cache_sharing_service.py`)

```python
"""
Cache sharing service for aicache team management
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import hashlib

from ..utils.logger import get_logger

logger = get_logger(__name__)

class CacheSharingService:
    """Manage shared cache entries for teams"""
    
    def __init__(self):
        self.shared_entries = {}  # cache_key -> sharing info
        self.team_shared_entries = {}  # team_id -> [cache_keys]
        
    async def share_cache_entry(
        self,
        cache_key: str,
        team_id: str,
        shared_by: str,
        permissions: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Share a cache entry with a team"""
        try:
            # Create sharing record
            sharing_id = hashlib.sha256(f"{cache_key}_{team_id}_{shared_by}".encode()).hexdigest()[:16]
            
            sharing_info = {
                'id': sharing_id,
                'cache_key': cache_key,
                'team_id': team_id,
                'shared_by': shared_by,
                'permissions': permissions or {'read': True, 'write': False},
                'shared_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            # Store sharing information
            self.shared_entries[sharing_id] = sharing_info
            
            # Update team shared entries
            if team_id not in self.team_shared_entries:
                self.team_shared_entries[team_id] = []
            if cache_key not in self.team_shared_entries[team_id]:
                self.team_shared_entries[team_id].append(cache_key)
                
            logger.info(f"Cache entry {cache_key[:8]}... shared with team {team_id}")
            
            return sharing_info
            
        except Exception as e:
            logger.error(f"Error sharing cache entry: {e}")
            raise
            
    async def unshare_cache_entry(
        self,
        cache_key: str,
        team_id: str
    ) -> bool:
        """Unshare a cache entry from a team"""
        try:
            # Find sharing record
            sharing_id = None
            for sid, sharing_info in self.shared_entries.items():
                if sharing_info['cache_key'] == cache_key and sharing_info['team_id'] == team_id:
                    sharing_id = sid
                    break
                    
            if sharing_id:
                del self.shared_entries[sharing_id]
                
                # Update team shared entries
                if team_id in self.team_shared_entries:
                    if cache_key in self.team_shared_entries[team_id]:
                        self.team_shared_entries[team_id].remove(cache_key)
                        
                logger.info(f"Cache entry {cache_key[:8]}... unshared from team {team_id}")
                return True
                
            logger.warning(f"No sharing record found for cache entry {cache_key[:8]}... in team {team_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error unsharing cache entry: {e}")
            raise
            
    async def get_team_shared_entries(self, team_id: str) -> List[Dict[str, Any]]:
        """Get all cache entries shared with a team"""
        try:
            if team_id not in self.team_shared_entries:
                return []
                
            shared_entries = []
            for cache_key in self.team_shared_entries[team_id]:
                # Find sharing info for this cache key
                for sharing_info in self.shared_entries.values():
                    if sharing_info['cache_key'] == cache_key and sharing_info['team_id'] == team_id:
                        shared_entries.append(sharing_info)
                        break
                        
            return shared_entries
            
        except Exception as e:
            logger.error(f"Error getting team shared entries: {e}")
            raise
            
    async def get_user_shared_entries(self, user_id: str, team_id: str) -> List[Dict[str, Any]]:
        """Get cache entries shared with a user in a team"""
        # In a real implementation, this would check user-specific permissions
        # For now, return all team shared entries
        return await self.get_team_shared_entries(team_id)
        
    async def update_sharing_permissions(
        self,
        cache_key: str,
        team_id: str,
        permissions: Dict[str, Any]
    ) -> bool:
        """Update sharing permissions for a cache entry"""
        try:
            # Find sharing record
            sharing_id = None
            for sid, sharing_info in self.shared_entries.items():
                if sharing_info['cache_key'] == cache_key and sharing_info['team_id'] == team_id:
                    sharing_id = sid
                    break
                    
            if sharing_id:
                self.shared_entries[sharing_id]['permissions'] = permissions
                logger.info(f"Sharing permissions updated for cache entry {cache_key[:8]}... in team {team_id}")
                return True
                
            logger.warning(f"No sharing record found for cache entry {cache_key[:8]}... in team {team_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error updating sharing permissions: {e}")
            raise
            
    async def can_user_access_shared_entry(
        self,
        user_id: str,
        cache_key: str,
        team_id: str,
        action: str = "read"
    ) -> bool:
        """Check if user can access a shared cache entry"""
        try:
            # Find sharing record
            for sharing_info in self.shared_entries.values():
                if (sharing_info['cache_key'] == cache_key and 
                    sharing_info['team_id'] == team_id):
                    
                    permissions = sharing_info['permissions']
                    return permissions.get(action, False)
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking access permissions: {e}")
            return False
```

## Notification Service (`src/services/notification_service.py`)

```python
"""
Notification service for aicache team management
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import json

from ..utils.logger import get_logger

logger = get_logger(__name__)

class NotificationService:
    """Send and manage notifications for team activities"""
    
    def __init__(self):
        self.notification_channels = {
            'email': [],
            'slack': [],
            'discord': [],
            'sms': [],
            'push': []
        }
        self.user_preferences = {}  # user_id -> preferences
        self.pending_notifications = []
        
    async def send_notification(
        self,
        recipients: List[str],
        message: str,
        notification_type: str = "info",
        channel: str = "email",
        metadata: Dict[str, Any] = None
    ):
        """Send notification to recipients"""
        try:
            notification = {
                'id': f"notif_{len(self.pending_notifications) + 1}",
                'recipients': recipients,
                'message': message,
                'type': notification_type,
                'channel': channel,
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            self.pending_notifications.append(notification)
            
            # Send based on channel
            if channel == 'email':
                await self._send_email_notification(notification)
            elif channel == 'slack':
                await self._send_slack_notification(notification)
            elif channel == 'discord':
                await self._send_discord_notification(notification)
            elif channel == 'sms':
                await self._send_sms_notification(notification)
            elif channel == 'push':
                await self._send_push_notification(notification)
            else:
                logger.warning(f"Unknown notification channel: {channel}")
                
            # Update status
            notification['status'] = 'sent'
            logger.info(f"Notification sent to {len(recipients)} recipients via {channel}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            raise
            
    async def _send_email_notification(self, notification: Dict[str, Any]):
        """Send email notification"""
        # In a real implementation, this would use an email service
        logger.debug(f"Email notification prepared: {notification['message'][:50]}...")
        
    async def _send_slack_notification(self, notification: Dict[str, Any]):
        """Send Slack notification"""
        # In a real implementation, this would use Slack API
        logger.debug(f"Slack notification prepared: {notification['message'][:50]}...")
        
    async def _send_discord_notification(self, notification: Dict[str, Any]):
        """Send Discord notification"""
        # In a real implementation, this would use Discord API
        logger.debug(f"Discord notification prepared: {notification['message'][:50]}...")
        
    async def _send_sms_notification(self, notification: Dict[str, Any]):
        """Send SMS notification"""
        # In a real implementation, this would use SMS service
        logger.debug(f"SMS notification prepared: {notification['message'][:50]}...")
        
    async def _send_push_notification(self, notification: Dict[str, Any]):
        """Send push notification"""
        # In a real implementation, this would use push notification service
        logger.debug(f"Push notification prepared: {notification['message'][:50]}...")
        
    async def set_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ):
        """Set user notification preferences"""
        try:
            self.user_preferences[user_id] = preferences
            logger.info(f"Notification preferences updated for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error setting user preferences: {e}")
            raise
            
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        return self.user_preferences.get(user_id, {
            'email': True,
            'slack': False,
            'discord': False,
            'sms': False,
            'push': True
        })
        
    async def broadcast_team_notification(
        self,
        team_id: str,
        message: str,
        notification_type: str = "info",
        exclude_users: List[str] = None
    ):
        """Broadcast notification to all team members"""
        try:
            # In a real implementation, this would get actual team members
            # For now, we'll use placeholder recipients
            recipients = [f"user_{i}" for i in range(1, 6)]  # Placeholder users
            
            # Exclude specified users
            if exclude_users:
                recipients = [r for r in recipients if r not in exclude_users]
                
            # Send to each user with their preferred channels
            for user_id in recipients:
                preferences = await self.get_user_preferences(user_id)
                
                # Send via preferred channels
                for channel, enabled in preferences.items():
                    if enabled:
                        await self.send_notification(
                            recipients=[user_id],
                            message=message,
                            notification_type=notification_type,
                            channel=channel
                        )
                        
            logger.info(f"Team notification broadcast to {len(recipients)} members")
            
        except Exception as e:
            logger.error(f"Error broadcasting team notification: {e}")
            raise
            
    async def create_alert(
        self,
        team_id: str,
        alert_type: str,
        message: str,
        severity: str = "medium"
    ):
        """Create and send alert notification"""
        try:
            alert_message = f"[{severity.upper()}] {alert_type}: {message}"
            
            await self.broadcast_team_notification(
                team_id=team_id,
                message=alert_message,
                notification_type="alert"
            )
            
            logger.info(f"Alert created for team {team_id}: {alert_type}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise
            
    async def cleanup_old_notifications(self, days_old: int = 30):
        """Clean up old notifications"""
        try:
            now = datetime.now()
            old_notifications = []
            
            for notification in self.pending_notifications:
                created_at_str = notification['created_at']
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                days_since_created = (now - created_at).days
                
                if days_since_created > days_old:
                    old_notifications.append(notification)
                    
            # Remove old notifications
            for notification in old_notifications:
                self.pending_notifications.remove(notification)
                
            logger.info(f"Cleaned up {len(old_notifications)} old notifications")
            
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {e}")
```

## Team Analytics (`src/services/team_analytics.py`)

```python
"""
Team analytics service for aicache team management
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from ..utils.logger import get_logger

logger = get_logger(__name__)

class TeamAnalytics:
    """Calculate and track team performance metrics"""
    
    def __init__(self):
        self.team_metrics = {}  # team_id -> metrics
        self.user_metrics = {}  # user_id -> metrics
        self.activity_logs = []  # Historical activity data
        
    async def calculate_team_metrics(self, team_id: str) -> Dict[str, Any]:
        """Calculate performance metrics for a team"""
        try:
            # In a real implementation, this would query actual data
            # For now, we'll generate sample metrics
            
            # Generate sample metrics
            metrics = {
                'team_id': team_id,
                'active_members': np.random.randint(3, 15),
                'total_cache_queries': np.random.randint(100, 1000),
                'cache_hit_rate': round(np.random.uniform(0.7, 0.95), 3),
                'avg_response_time': round(np.random.uniform(0.05, 0.3), 3),
                'shared_entries': np.random.randint(10, 100),
                'collaboration_score': round(np.random.uniform(0.6, 0.9), 3),
                'productivity_score': round(np.random.uniform(0.7, 0.9), 3),
                'calculated_at': datetime.now().isoformat()
            }
            
            # Store metrics
            self.team_metrics[team_id] = metrics
            
            logger.info(f"Metrics calculated for team {team_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating team metrics: {e}")
            raise
            
    async def calculate_user_metrics(self, user_id: str) -> Dict[str, Any]:
        """Calculate performance metrics for a user"""
        try:
            # Generate sample user metrics
            metrics = {
                'user_id': user_id,
                'queries_made': np.random.randint(10, 200),
                'cache_contributions': np.random.randint(5, 50),
                'collaboration_events': np.random.randint(10, 100),
                'activity_score': round(np.random.uniform(0.6, 1.0), 3),
                'efficiency_score': round(np.random.uniform(0.7, 0.95), 3),
                'calculated_at': datetime.now().isoformat()
            }
            
            # Store metrics
            self.user_metrics[user_id] = metrics
            
            logger.info(f"Metrics calculated for user {user_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating user metrics: {e}")
            raise
            
    async def get_team_trends(self, team_id: str, period: str = "7d") -> Dict[str, Any]:
        """Get team performance trends"""
        try:
            # Generate sample trend data
            days = 7 if period == "7d" else 30
            
            trends = {
                'period': period,
                'cache_hit_rate': [round(np.random.uniform(0.7, 0.95), 3) for _ in range(days)],
                'response_time': [round(np.random.uniform(0.05, 0.3), 3) for _ in range(days)],
                'active_users': [np.random.randint(2, 12) for _ in range(days)],
                'shared_entries': [np.random.randint(5, 50) for _ in range(days)]
            }
            
            logger.info(f"Trends generated for team {team_id} over {period}")
            return trends
            
        except Exception as e:
            logger.error(f"Error generating team trends: {e}")
            raise
            
    async def get_productivity_insights(self, team_id: str) -> List[Dict[str, Any]]:
        """Get productivity insights for a team"""
        try:
            # Generate sample insights
            insights = [
                {
                    'type': 'recommendation',
                    'title': 'Increase Cache Usage',
                    'description': 'Team cache hit rate is below optimal threshold',
                    'severity': 'medium',
                    'action': 'Encourage more cache usage in daily workflows'
                },
                {
                    'type': 'observation',
                    'title': 'High Collaboration',
                    'description': 'Team shows strong collaborative behavior',
                    'severity': 'positive',
                    'action': 'Continue fostering collaborative culture'
                },
                {
                    'type': 'opportunity',
                    'title': 'Expand Shared Knowledge',
                    'description': 'Opportunity to share more cache entries across team',
                    'severity': 'low',
                    'action': 'Identify frequently used patterns for sharing'
                }
            ]
            
            logger.info(f"Productivity insights generated for team {team_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating productivity insights: {e}")
            raise
            
    async def get_benchmark_comparison(self, team_id: str) -> Dict[str, Any]:
        """Compare team performance against benchmarks"""
        try:
            # Get current metrics
            current_metrics = self.team_metrics.get(team_id)
            if not current_metrics:
                current_metrics = await self.calculate_team_metrics(team_id)
                
            # Generate benchmark comparison
            benchmark_comparison = {
                'team_metrics': current_metrics,
                'industry_benchmarks': {
                    'cache_hit_rate': 0.82,
                    'avg_response_time': 0.15,
                    'collaboration_score': 0.75
                },
                'comparison': {
                    'cache_hit_rate_vs_benchmark': round(current_metrics['cache_hit_rate'] - 0.82, 3),
                    'response_time_vs_benchmark': round(0.15 - current_metrics['avg_response_time'], 3),
                    'collaboration_vs_benchmark': round(current_metrics['collaboration_score'] - 0.75, 3)
                },
                'performance_category': 'above_average' if current_metrics['cache_hit_rate'] > 0.82 else 'average'
            }
            
            logger.info(f"Benchmark comparison generated for team {team_id}")
            return benchmark_comparison
            
        except Exception as e:
            logger.error(f"Error generating benchmark comparison: {e}")
            raise
            
    async def log_activity(self, activity_data: Dict[str, Any]):
        """Log team activity for analytics"""
        try:
            activity_record = {
                'timestamp': datetime.now().isoformat(),
                'activity_type': activity_data.get('type'),
                'team_id': activity_data.get('team_id'),
                'user_id': activity_data.get('user_id'),
                'details': activity_data.get('details', {}),
                'impact_score': activity_data.get('impact_score', 0)
            }
            
            self.activity_logs.append(activity_record)
            
            # Keep only recent activities (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            self.activity_logs = [
                log for log in self.activity_logs 
                if datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')) > cutoff_date
            ]
            
            logger.debug(f"Activity logged: {activity_data.get('type')}")
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            
    async def generate_team_report(self, team_id: str) -> Dict[str, Any]:
        """Generate comprehensive team performance report"""
        try:
            # Get all relevant data
            current_metrics = await self.calculate_team_metrics(team_id)
            trends = await self.get_team_trends(team_id)
            insights = await self.get_productivity_insights(team_id)
            benchmark_comparison = await self.get_benchmark_comparison(team_id)
            
            # Generate report
            report = {
                'team_id': team_id,
                'generated_at': datetime.now().isoformat(),
                'period': 'Last 7 days',
                'executive_summary': {
                    'overall_performance': 'Good',
                    'key_strengths': ['Strong collaboration', 'Good cache usage'],
                    'areas_for_improvement': ['Increase cache hit rate']
                },
                'detailed_metrics': current_metrics,
                'trends': trends,
                'insights': insights,
                'benchmark_comparison': benchmark_comparison,
                'recommendations': [
                    'Continue promoting collaborative cache sharing',
                    'Provide training on advanced cache query techniques',
                    'Implement team-specific cache optimization strategies'
                ]
            }
            
            logger.info(f"Team report generated for team {team_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating team report: {e}")
            raise
```

## Activity Feed (`src/services/activity_feed.py`)

```python
"""
Activity feed service for aicache team management
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

from ..utils.logger import get_logger

logger = get_logger(__name__)

class ActivityFeed:
    """Aggregate and serve team activity feeds"""
    
    def __init__(self):
        self.activities = []  # All activities
        self.team_activities = defaultdict(list)  # team_id -> activities
        self.user_activities = defaultdict(list)  # user_id -> activities
        
    async def log_activity(
        self,
        activity_type: str,
        team_id: str,
        user_id: str,
        description: str,
        details: Dict[str, Any] = None,
        impact_score: float = 1.0
    ):
        """Log a team activity"""
        try:
            activity = {
                'id': f"activity_{len(self.activities) + 1}",
                'type': activity_type,
                'team_id': team_id,
                'user_id': user_id,
                'description': description,
                'details': details or {},
                'impact_score': impact_score,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store activity
            self.activities.append(activity)
            self.team_activities[team_id].append(activity)
            self.user_activities[user_id].append(activity)
            
            # Clean up old activities (keep last 1000 activities)
            if len(self.activities) > 1000:
                oldest_activity = self.activities.pop(0)
                team_id_oldest = oldest_activity['team_id']
                user_id_oldest = oldest_activity['user_id']
                
                # Remove from team and user collections
                if team_id_oldest in self.team_activities:
                    self.team_activities[team_id_oldest] = [
                        a for a in self.team_activities[team_id_oldest] 
                        if a['id'] != oldest_activity['id']
                    ]
                if user_id_oldest in self.user_activities:
                    self.user_activities[user_id_oldest] = [
                        a for a in self.user_activities[user_id_oldest] 
                        if a['id'] != oldest_activity['id']
                    ]
                    
            logger.info(f"Activity logged: {activity_type} for team {team_id}")
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            raise
            
    async def get_team_feed(
        self,
        team_id: str,
        limit: int = 50,
        activity_types: List[str] = None,
        time_window: str = "7d"
    ) -> List[Dict[str, Any]]:
        """Get activity feed for a team"""
        try:
            # Filter activities for team
            team_acts = self.team_activities.get(team_id, [])
            
            # Apply time window filter
            cutoff_time = datetime.now() - timedelta(
                days=7 if time_window == "7d" else 30
            )
            
            filtered_activities = [
                activity for activity in team_acts
                if datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00')) > cutoff_time
            ]
            
            # Apply activity type filter
            if activity_types:
                filtered_activities = [
                    activity for activity in filtered_activities
                    if activity['type'] in activity_types
                ]
                
            # Sort by timestamp (newest first)
            filtered_activities.sort(
                key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')),
                reverse=True
            )
            
            # Apply limit
            return filtered_activities[:limit]
            
        except Exception as e:
            logger.error(f"Error getting team feed: {e}")
            raise
            
    async def get_user_feed(
        self,
        user_id: str,
        limit: int = 50,
        activity_types: List[str] = None,
        time_window: str = "7d"
    ) -> List[Dict[str, Any]]:
        """Get activity feed for a user"""
        try:
            # Filter activities for user
            user_acts = self.user_activities.get(user_id, [])
            
            # Apply time window filter
            cutoff_time = datetime.now() - timedelta(
                days=7 if time_window == "7d" else 30
            )
            
            filtered_activities = [
                activity for activity in user_acts
                if datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00')) > cutoff_time
            ]
            
            # Apply activity type filter
            if activity_types:
                filtered_activities = [
                    activity for activity in filtered_activities
                    if activity['type'] in activity_types
                ]
                
            # Sort by timestamp (newest first)
            filtered_activities.sort(
                key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')),
                reverse=True
            )
            
            # Apply limit
            return filtered_activities[:limit]
            
        except Exception as e:
            logger.error(f"Error getting user feed: {e}")
            raise
            
    async def get_recent_activities(
        self,
        limit: int = 20,
        activity_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get most recent activities across all teams"""
        try:
            # Filter activities
            filtered_activities = self.activities.copy()
            
            # Apply activity type filter
            if activity_types:
                filtered_activities = [
                    activity for activity in filtered_activities
                    if activity['type'] in activity_types
                ]
                
            # Sort by timestamp (newest first)
            filtered_activities.sort(
                key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')),
                reverse=True
            )
            
            # Apply limit
            return filtered_activities[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent activities: {e}")
            raise
            
    async def get_activity_summary(
        self,
        team_id: str,
        time_window: str = "7d"
    ) -> Dict[str, Any]:
        """Get activity summary for a team"""
        try:
            # Get team activities
            team_acts = await self.get_team_feed(
                team_id=team_id,
                time_window=time_window
            )
            
            if not team_acts:
                return {
                    'total_activities': 0,
                    'activity_types': {},
                    'top_contributors': [],
                    'time_range': time_window
                }
                
            # Calculate summary statistics
            activity_counts = defaultdict(int)
            contributor_counts = defaultdict(int)
            
            for activity in team_acts:
                activity_counts[activity['type']] += 1
                contributor_counts[activity['user_id']] += 1
                
            # Get top contributors
            top_contributors = sorted(
                contributor_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            summary = {
                'total_activities': len(team_acts),
                'activity_types': dict(activity_counts),
                'top_contributors': [
                    {'user_id': user_id, 'activity_count': count}
                    for user_id, count in top_contributors
                ],
                'time_range': time_window,
                'most_active_period': self._get_most_active_period(team_acts)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting activity summary: {e}")
            raise
            
    def _get_most_active_period(self, activities: List[Dict[str, Any]]) -> str:
        """Determine the most active time period"""
        if not activities:
            return "unknown"
            
        # Count activities by hour of day
        hour_counts = defaultdict(int)
        for activity in activities:
            timestamp = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
            hour_counts[timestamp.hour] += 1
            
        # Find most active hour
        most_active_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        
        # Map to time period
        if 9 <= most_active_hour < 12:
            return "morning"
        elif 12 <= most_active_hour < 17:
            return "afternoon"
        elif 17 <= most_active_hour < 21:
            return "evening"
        else:
            return "night"
            
    async def search_activities(
        self,
        query: str,
        team_id: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search activities by query text"""
        try:
            # Filter activities
            if team_id:
                activities = self.team_activities.get(team_id, [])
            else:
                activities = self.activities
                
            # Search by query
            matching_activities = [
                activity for activity in activities
                if query.lower() in activity['description'].lower() or
                   query.lower() in str(activity['details']).lower()
            ]
            
            # Sort by relevance and timestamp
            matching_activities.sort(
                key=lambda x: (
                    datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00'))
                ),
                reverse=True
            )
            
            # Apply limit
            return matching_activities[:limit]
            
        except Exception as e:
            logger.error(f"Error searching activities: {e}")
            raise
            
    async def get_activity_stats(self) -> Dict[str, Any]:
        """Get overall activity statistics"""
        try:
            if not self.activities:
                return {
                    'total_activities': 0,
                    'total_teams': 0,
                    'total_users': 0,
                    'activity_growth_rate': 0.0
                }
                
            # Calculate statistics
            total_activities = len(self.activities)
            total_teams = len(self.team_activities)
            total_users = len(self.user_activities)
            
            # Calculate growth rate (last week vs week before)
            now = datetime.now()
            last_week_start = now - timedelta(days=7)
            week_before_start = now - timedelta(days=14)
            
            last_week_activities = [
                activity for activity in self.activities
                if (week_before_start <= 
                    datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00')) < 
                    last_week_start)
            ]
            
            week_before_activities = [
                activity for activity in self.activities
                if datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00')) < week_before_start
            ]
            
            if week_before_activities:
                growth_rate = (
                    (len(last_week_activities) - len(week_before_activities)) / 
                    len(week_before_activities) * 100
                )
            else:
                growth_rate = 0.0
                
            stats = {
                'total_activities': total_activities,
                'total_teams': total_teams,
                'total_users': total_users,
                'activity_growth_rate': round(growth_rate, 2),
                'most_popular_activity_type': self._get_most_popular_activity_type()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting activity stats: {e}")
            raise
            
    def _get_most_popular_activity_type(self) -> str:
        """Get the most popular activity type"""
        if not self.activities:
            return "unknown"
            
        activity_counts = defaultdict(int)
        for activity in self.activities:
            activity_counts[activity['type']] += 1
            
        return max(activity_counts.items(), key=lambda x: x[1])[0]
```

## Key Features Implementation

### 1. Real-time Presence Tracking
- WebSocket-based presence updates
- Activity monitoring and broadcasting
- Online/offline status management
- Team presence visualization

### 2. Collaborative Cache Sharing
- Team-based cache entry sharing
- Granular permission management
- Shared entry discovery and search
- Cross-team collaboration features

### 3. Notification System
- Multi-channel notification delivery
- User preference management
- Team-wide announcements
- Alert escalation and routing

### 4. Team Analytics and Insights
- Performance metrics calculation
- Productivity trend analysis
- Benchmark comparisons
- Actionable insights and recommendations

### 5. Activity Feed and History
- Comprehensive activity logging
- Searchable activity feeds
- Team and user-specific views
- Activity summarization and reporting

## Usage Examples

### 1. Create a Team
```python
import asyncio
from src.controllers.team_controller import create_team
from src.services.team_service import TeamService

async def create_sample_team():
    # Create team service
    team_service = TeamService()
    
    # Create a new team
    team = await team_service.create_team(
        name="Dev Team Alpha",
        description="Frontend development team",
        visibility="private",
        creator_id="user_123"
    )
    
    print(f"Created team: {team['name']}")
    return team

# Run the example
# asyncio.run(create_sample_team())
```

### 2. Add User to Team
```python
from src.services.user_service import UserService

async def add_user_to_team():
    user_service = UserService()
    
    # Add user to team
    membership = await user_service.add_user_to_team(
        user_id="user_456",
        team_id="team_abc123",
        role="developer"
    )
    
    print(f"Added user to team: {membership['user_id']}")
    return membership

# Run the example
# asyncio.run(add_user_to_team())
```

### 3. Log Team Activity
```python
from src.services.activity_feed import ActivityFeed

async def log_team_activity():
    activity_feed = ActivityFeed()
    
    # Log an activity
    await activity_feed.log_activity(
        activity_type="cache_query",
        team_id="team_abc123",
        user_id="user_123",
        description="User queried cache for React hooks tutorial",
        details={
            "query": "React hooks tutorial",
            "cache_hit": True,
            "response_time": 0.08
        },
        impact_score=0.7
    )
    
    print("Activity logged successfully")

# Run the example
# asyncio.run(log_team_activity())
```

### 4. Send Team Notification
```python
from src.services.notification_service import NotificationService

async def send_team_notification():
    notification_service = NotificationService()
    
    # Send notification to team
    await notification_service.broadcast_team_notification(
        team_id="team_abc123",
        message="New cache entry available: Python async/await tutorial",
        notification_type="info"
    )
    
    print("Team notification sent")

# Run the example
# asyncio.run(send_team_notification())
```

### 5. Calculate Team Metrics
```python
from src.services.team_analytics import TeamAnalytics

async def calculate_team_metrics():
    analytics = TeamAnalytics()
    
    # Calculate team metrics
    metrics = await analytics.calculate_team_metrics("team_abc123")
    
    print(f"Team metrics: {metrics}")
    return metrics

# Run the example
# asyncio.run(calculate_team_metrics())
```

## Integration with Other Systems

### Cache System Integration
- Real-time cache usage tracking
- Performance metric collection
- Cache entry sharing and discovery
- Usage pattern analysis

### Authentication Integration
- OAuth provider integration
- LDAP/Active Directory support
- Single sign-on (SSO) compatibility
- Multi-factor authentication support

### Communication Platform Integration
- Slack integration for notifications
- Discord integration for team chat
- Email integration for formal communications
- SMS integration for critical alerts

### Analytics Platform Integration
- Google Analytics for web analytics
- Mixpanel for user behavior tracking
- Amplitude for product analytics
- Custom dashboard integration

## Security Implementation

### Access Control
- Role-based access control (RBAC)
- Permission inheritance and delegation
- Team and project-level permissions
- Audit logging for compliance

### Data Protection
- End-to-end encryption for communications
- Data encryption at rest
- Secure credential storage
- Privacy-preserving analytics

### Authentication
- Multi-factor authentication support
- OAuth 2.0 integration
- SAML-based single sign-on
- Session management and expiration

## Performance Optimization

### Caching Strategies
- In-memory caching for frequently accessed data
- Database query result caching
- API response caching
- CDN integration for static assets

### Database Optimization
- Index optimization for fast queries
- Connection pooling for efficient access
- Read replicas for scaling
- Query optimization and planning

### Real-time Communication
- WebSocket connection management
- Message batching for efficiency
- Connection keep-alive strategies
- Load balancing for high availability

## Monitoring and Observability

### Application Metrics
- API response time monitoring
- Database query performance
- Cache hit/miss ratios
- User session tracking

### Infrastructure Metrics
- CPU and memory utilization
- Network I/O monitoring
- Disk space utilization
- Container health status

### Logging and Tracing
- Structured logging for analysis
- Distributed tracing for request flow
- Error rate monitoring
- Performance bottleneck identification

## Deployment Architecture

### Containerized Deployment
```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                        │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ API Server  │  │ API Server  │  │ API Server  │  ... │
│  │ Container   │  │ Container   │  │ Container   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ WebSocket   │  │ WebSocket   │  │ WebSocket   │  ... │
│  │ Server      │  │ Server      │  │ Server      │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Database    │  │ Cache       │  │ Message     │      │
│  │ Container   │  │ Container   │  │ Broker      │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────┘
```

### Kubernetes Deployment
- Horizontal pod autoscaling
- Rolling updates for zero-downtime deployments
- Health checks and readiness probes
- Resource limits and requests
- Persistent volume claims for data

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: Deploy Team Management
on:
  push:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          python -m pytest tests/
  
  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: |
          docker build -t aicache/team-management ./src
  
  deploy:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f kubernetes/team-management.yaml
```

This team management interface provides comprehensive collaboration features for aicache, enabling teams to work together effectively while maintaining security and performance.