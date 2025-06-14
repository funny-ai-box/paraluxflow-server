# app/api/client/v1/__init__.py
from flask import Blueprint

# 创建API v1客户端主蓝图
api_client_v1_bp = Blueprint("api_client_v1", __name__)

# 导入认证相关蓝图
from app.api.client.v1.auth.auth import auth_bp
# 导入RSS相关蓝图
from app.api.client.v1.rss import rss_bp
# 导入用户相关蓝图
from app.api.client.v1.user import user_bp
from app.api.client.v1.assistant import assistant_bp
# 导入订阅相关蓝图
from app.api.client.v1.subscription.subscription import subscription_bp
# 导入热点话题蓝图
from app.api.client.v1.hot_topics.hot_topics import client_hot_topics_bp

# 注册认证蓝图
api_client_v1_bp.register_blueprint(auth_bp, url_prefix="/auth")

# 注册RSS蓝图
api_client_v1_bp.register_blueprint(rss_bp, url_prefix="/rss")

# 注册用户蓝图
api_client_v1_bp.register_blueprint(user_bp, url_prefix="/user")


# 注册订阅蓝图
api_client_v1_bp.register_blueprint(subscription_bp, url_prefix="/subscription")
api_client_v1_bp.register_blueprint(assistant_bp, url_prefix="/assistant")
# 注册热点话题蓝图
api_client_v1_bp.register_blueprint(client_hot_topics_bp, url_prefix="/hot_topic")