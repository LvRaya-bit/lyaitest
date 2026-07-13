# ============================================
# 1. 导入依赖
# ============================================
import streamlit as st          # Web界面框架
import requests                 # 用于调用后端API

# ============================================
# 2. 页面配置
# ============================================
st.set_page_config(
    page_title="LYAITEST AI测试平台",   # 浏览器标签页标题
    page_icon="🤖"                      # 浏览器标签页图标
)
st.title("🤖 LYAITEST AI测试平台")      # 页面顶部大标题
st.write("欢迎使用 LYAITEST！")         # 页面副标题

# ============================================
# 3. 初始化会话状态（session_state）
# ============================================
# Streamlit 每次用户操作都会重新运行整个脚本
# st.session_state 用来保存变量，让数据在多次运行间不丢失

if "session_id" not in st.session_state:
    st.session_state.session_id = None      # 当前选中的会话ID
if "messages" not in st.session_state:
    st.session_state.messages = []          # 当前会话的聊天历史
if "sessions" not in st.session_state:
    st.session_state.sessions = []          # 所有会话列表
if "reports" not in st.session_state:
    st.session_state.reports = []           # 所有测试报告列表
if "selected_report" not in st.session_state:
    st.session_state.selected_report = None # 当前选中的报告详情

# ============================================
# 4. 后端 API 地址
# ============================================
# 本地开发
#API_BASE = "http://localhost:8000/api/v1"   # 后端服务地址
# 生产环境（替换成你的 Render URL）
API_BASE = "https://lyaitest.onrender.com/api/v1"

# ============================================
# 5. 侧边栏（左侧面板）
# ============================================
with st.sidebar:
    st.header("📋 会话管理")
    
    # ---------- 5.1 创建会话 ----------
    st.subheader("🆕 创建新会话")
    session_name = st.text_input("会话名称", placeholder="输入会话名称...")
    
    if st.button("创建会话"):
        if session_name:
            try:
                # 调用后端API创建会话
                response = requests.post(
                    f"{API_BASE}/sessions/",
                    json={"name": session_name}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data["session_id"]
                    st.success(f"✅ 会话已创建：{data['session_id']}")
                else:
                    st.error("❌ 创建失败")
            except Exception as e:
                st.error(f"❌ 连接失败：{e}")
        else:
            st.warning("⚠️ 请输入会话名称")
    
    st.divider()  # 分割线
    
    # ---------- 5.2 获取会话列表 ----------
    st.subheader("📂 已有会话")
    
    if st.button("刷新会话列表"):
        try:
            response = requests.get(f"{API_BASE}/sessions/")
            if response.status_code == 200:
                st.session_state.sessions = response.json()
                st.success(f"✅ 已加载 {len(st.session_state.sessions)} 个会话")
            else:
                st.error("❌ 加载失败")
        except Exception as e:
            st.error(f"❌ 连接失败：{e}")
    
    # 显示所有会话，每个会话一行，带删除按钮
    for s in st.session_state.sessions:
        col1, col2 = st.columns([4, 1])  # 分两列，左侧占4份，右侧占1份
        
        with col1:
            # 点击会话名称，切换当前会话
            if st.button(f"📌 {s['name']}", key=s["session_id"]):
                st.session_state.session_id = s["session_id"]
                st.session_state.messages = []  # 清空聊天记录
                st.rerun()  # 刷新页面
        
        with col2:
            # 删除会话按钮
            if st.button("🗑️", key=f"del_{s['session_id']}"):
                try:
                    response = requests.delete(
                        f"{API_BASE}/sessions/{s['session_id']}"
                    )
                    if response.status_code == 200:
                        # 从列表中移除
                        st.session_state.sessions = [
                            x for x in st.session_state.sessions 
                            if x["session_id"] != s["session_id"]
                        ]
                        # 如果删除的是当前会话，清空状态
                        if st.session_state.session_id == s["session_id"]:
                            st.session_state.session_id = None
                            st.session_state.messages = []
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ 删除失败：{e}")
    
    st.divider()
    
    # ---------- 5.3 测试报告 ----------
    # ---------- 5.3 测试报告 ----------
st.header("📊 测试报告")

# 刷新按钮
if st.button("刷新报告列表"):
    try:
        response = requests.get(f"{API_BASE}/reports/")
        if response.status_code == 200:
            st.session_state.reports = response.json()
            st.success(f"✅ 已加载 {len(st.session_state.reports)} 条报告")
        else:
            st.error("❌ 加载失败")
    except Exception as e:
        st.error(f"❌ 连接失败：{e}")

# 获取所有报告
all_reports = st.session_state.reports

if all_reports:
    # 构建会话列表（用于筛选）
    session_ids = list(set(r.get("session_id", "unknown") for r in all_reports))
    session_options = ["全部报告"] + session_ids
    
    # 筛选下拉框
    selected_session_filter = st.selectbox(
        "筛选会话",
        session_options,
        key="report_filter"
    )
    
    # 根据筛选条件过滤报告
    if selected_session_filter == "全部报告":
        filtered_reports = all_reports
    else:
        filtered_reports = [r for r in all_reports if r.get("session_id") == selected_session_filter]
    
    st.info(f"📌 共 {len(filtered_reports)} 条测试报告")
    
    # 显示过滤后的报告列表
    for r in filtered_reports:
        if st.button(
            f"📄 {r['test_type']} - {r['url'][:30]}...",
            key=f"report_{r['id']}"
        ):
            st.session_state.selected_report = r
            st.rerun()
else:
    st.caption("暂无测试报告")
    
    # 显示报告列表，每条报告作为一个按钮
    if st.session_state.reports:
        st.info(f"📌 共 {len(st.session_state.reports)} 条测试报告")
        for r in st.session_state.reports:
            # 点击报告查看详情
            if st.button(
                f"📄 {r['test_type']} - {r['url'][:30]}...",  # 显示类型和URL前30个字符
                key=f"report_{r['id']}"
            ):
                st.session_state.selected_report = r  # 保存选中的报告
                st.rerun()
    else:
        st.caption("暂无测试报告")

# ============================================
# 6. 主区域
# ============================================
st.divider()

# ---------- 6.1 如果选中了报告，显示报告详情 ----------
if st.session_state.selected_report:
    r = st.session_state.selected_report
    st.subheader("📄 测试报告详情")
    
    # 用两列布局显示报告信息
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**测试类型**: {r.get('test_type', 'N/A')}")
        st.write(f"**URL**: {r.get('url', 'N/A')}")
        st.write(f"**状态码**: {r.get('status_code', 'N/A')}")
    with col2:
        st.write(f"**页面标题**: {r.get('title', 'N/A')}")
        st.write(f"**截图路径**: {r.get('screenshot', 'N/A')}")
        st.write(f"**创建时间**: {r.get('created_at', 'N/A')}")
    
    # 如果有截图，显示截图预览
    if r.get('screenshot'):
        st.write("**截图预览**:")
        try:
            st.image(r['screenshot'], caption="测试截图", use_container_width=True)
        except Exception as e:
            st.warning(f"无法加载截图：{e}")
    
    # 关闭报告按钮
    if st.button("关闭报告"):
        st.session_state.selected_report = None
        st.rerun()

# ---------- 6.2 否则显示聊天界面 ----------
else:
    # 如果未选中会话，提示用户
    if st.session_state.session_id is None:
        st.info("👈 请先在左侧创建或选择一个会话")
    else:
        st.success(f"当前会话：{st.session_state.session_id}")
        
        # 显示聊天历史
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):  # role 为 "user" 或 "assistant"
                st.write(msg["content"])
        
        # 输入框
        user_input = st.chat_input("输入消息...")
        if user_input:
            # 显示用户消息
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            
            # 调用后端 Agent 接口
            try:
                response = requests.post(
                    f"{API_BASE}/agent/",
                    json={"message": user_input, "session_id": st.session_state.session_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    reply = data["reply"]
                    
                    # 显示 AI 回复
                    with st.chat_message("assistant"):
                        st.write(reply)
                    
                    # 保存到聊天历史
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                else:
                    st.error(f"❌ 请求失败：{response.status_code}")
            except Exception as e:
                st.error(f"❌ 连接失败：{e}")
