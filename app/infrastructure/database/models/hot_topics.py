# app/infrastructure/database/models/hot_topics.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float, func, Date, UniqueConstraint, Index

from app.extensions import db
from app.core.security import generate_uuid

class HotTopicTask(db.Model):
    """热点爬取任务模型"""
    __tablename__ = "hot_topic_tasks"

    id = Column(Integer, primary_key=True)
    task_id = Column(String(36), unique=True, nullable=False, comment="任务ID")
    status = Column(Integer, default=0, comment="状态：0=待爬取，1=爬取中，2=已完成，3=失败")
    platforms = Column(JSON, comment="需要爬取的平台列表：['weibo', 'zhihu', 'baidu', 'toutiao', 'douyin']")
    scheduled_time = Column(DateTime, comment="计划执行时间")
    crawler_id = Column(String(255), comment="爬虫标识")
    trigger_type = Column(String(20), comment="触发类型：scheduled=定时触发，manual=手动触发")
    triggered_by = Column(String(36), comment="触发用户ID")
    recurrence = Column(String(20), default="none", comment="重复类型：daily=每日, weekly=每周, monthly=每月, none=不重复")
    last_executed_at = Column(DateTime, comment="最后执行时间")
    next_execution_at = Column(DateTime, comment="下次执行时间")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class HotTopic(db.Model):
    """热点话题模型"""
    __tablename__ = "hot_topics"

    id = Column(Integer, primary_key=True)
    task_id = Column(String(36), nullable=False, comment="关联的任务ID")
    batch_id = Column(String(36), nullable=False, comment="批次ID")
    
    platform = Column(String(20), nullable=False, comment="平台：weibo, zhihu, baidu, toutiao, douyin")
    topic_title = Column(String(512), nullable=False, comment="话题标题")
    topic_url = Column(String(1024), comment="话题链接")
    hot_value = Column(String(128), comment="热度值")
    
    topic_description = Column(Text, comment="话题描述")
    is_hot = Column(Boolean, default=False, comment="是否标记为热门")
    is_new = Column(Boolean, default=False, comment="是否标记为新上榜")
    
    rank = Column(Integer, comment="排名")
    rank_change = Column(Integer, comment="排名变化")
    heat_level = Column(Integer, comment="热度等级：1-5")
    
    # 新增字段：热点日期
    topic_date = Column(Date, nullable=False, default=func.current_date(), comment="热点日期")
    
    # 新增：稳定的唯一标识符，用于关联聚合热点
    stable_hash = Column(String(64), nullable=False, index=True, comment="基于标题和平台生成的稳定哈希值")
    
    crawler_id = Column(String(255), comment="爬虫标识")
    crawl_time = Column(DateTime, comment="爬取时间")
    status = Column(Integer, default=1, comment="状态：1=有效，0=无效")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 修改唯一约束：同一日期、同一平台、同一稳定哈希不能重复
    __table_args__ = (
        UniqueConstraint('topic_date', 'platform', 'stable_hash', name='uix_topic_date_platform_hash'),
        Index('idx_stable_hash_date', 'stable_hash', 'topic_date'),  # 为查询优化添加索引
    )

class HotTopicLog(db.Model):
    """热点爬取日志模型"""
    __tablename__ = "hot_topic_logs"

    id = Column(Integer, primary_key=True)
    task_id = Column(String(36), nullable=False, comment="关联的任务ID")
    batch_id = Column(String(36), nullable=False, comment="批次ID")
    
    platform = Column(String(20), nullable=False, comment="平台：weibo, zhihu, baidu, toutiao, douyin")
    status = Column(Integer, nullable=False, comment="状态：1=成功，2=失败")
    
    topic_count = Column(Integer, default=0, comment="爬取到的话题数量")
    error_type = Column(String(50), comment="错误类型")
    error_stage = Column(String(50), comment="错误阶段")
    error_message = Column(Text, comment="错误信息")
    error_stack_trace = Column(Text, comment="错误堆栈")
    
    request_started_at = Column(DateTime, comment="请求开始时间")
    request_ended_at = Column(DateTime, comment="请求结束时间")
    request_duration = Column(Float, comment="请求耗时(秒)")
    
    processing_time = Column(Float, comment="处理时间(秒)")
    memory_usage = Column(Float, comment="内存使用(MB)")
    cpu_usage = Column(Float, comment="CPU使用率(%)")
    
    crawler_id = Column(String(255), comment="爬虫标识")
    crawler_host = Column(String(255), comment="爬虫主机名")
    crawler_ip = Column(String(50), comment="爬虫IP")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class UnifiedHotTopic(db.Model):
    """统一热点话题模型 (由AI聚合生成)"""
    __tablename__ = "unified_hot_topics"

    id = Column(String(32), primary_key=True, default=generate_uuid, comment="统一热点ID")
    topic_date = Column(Date, nullable=False, index=True, comment="热点所属日期")
    
    unified_title = Column(String(512), nullable=False, comment="AI生成的统一标题")
    unified_summary = Column(Text, comment="AI生成的统一摘要")
    representative_url = Column(String(1024), comment="代表性链接")
    
    # 关键词字段
    keywords = Column(JSON, comment="AI提取的关键词列表 ['关键词1', '关键词2', ...]")
    
    # 新增：分类字段
    category = Column(String(50), default="other", comment="内容分类 (politics/economy/technology等)")
    
    # 修改：存储稳定的哈希值而非易变的ID
    related_topic_hashes = Column(JSON, nullable=False, comment="关联的原始热点稳定哈希列表")
    # 保留原字段作为备用（可选）
    related_topic_ids = Column(JSON, comment="关联的原始HotTopic ID列表（备用）")
    
    # 存储来源平台列表
    source_platforms = Column(JSON, nullable=False, comment="来源平台列表 (e.g., ['weibo', 'zhihu'])")
    
    # 聚合热度信息
    aggregated_hotness_score = Column(Float, comment="聚合热度分")
    topic_count = Column(Integer, default=0, comment="关联的原始热点数量")

    # AI 处理信息
    ai_model_used = Column(String(100), comment="使用的AI模型")
    ai_processing_time = Column(Float, comment="AI处理耗时(秒)")

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<UnifiedHotTopic {self.unified_title} ({self.topic_date})>"

class HotTopicPlatform(db.Model):
    """热点平台模型"""
    __tablename__ = "hot_topic_platforms"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False, comment="平台标识码")
    name = Column(String(100), nullable=False, comment="平台名称")
    icon = Column(String(100), comment="平台图标 (例如 fa-weibo)")
    description = Column(String(255), comment="平台描述")
    url = Column(String(255), comment="平台URL")
    
    # 爬虫配置
    crawl_config = Column(JSON, comment="爬虫配置 (可选的 JSON 格式)")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否启用")
    last_crawl_at = Column(DateTime, comment="最近一次爬取时间")
    display_order = Column(Integer, default=100, comment="显示顺序 (从小到大排序)")
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<HotTopicPlatform {self.code}>"