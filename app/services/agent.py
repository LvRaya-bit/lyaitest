"""
LYAITEST Agent 核心模块
基于 LangGraph 构建的测试智能体，支持意图识别和工具调用
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_openai import ChatOpenAI
import os
import time
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import threading
import subprocess
import json

load_dotenv()

# ============================================
# 第1部分：状态定义（State）
# ============================================
class AgentState(TypedDict):
    """
    Agent 的"记忆"结构，所有节点共享这个状态
    
    字段说明：
    - messages: 对话历史列表，每一条包含 role 和 content
    - next_step: 下一步要执行的动作，由意图识别节点决定
    """
    messages: list           # [{"role": "user", "content": "..."}, ...]
    next_step: str           # "generate_case" | "run_api_test" | "run_web_test" | "chat"

# ============================================
# 第2部分：模型初始化
# ============================================
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com",
    temperature=0.3
)

# ============================================
# 第3部分：节点函数（Node）
# ============================================

# ---------- 节点1：意图识别 ----------
def identify_intent(state: AgentState):
    """
    用 LLM 判断用户意图，决定下一步走哪个节点
    
    输入：用户最新消息
    输出：设置 state["next_step"] = 目标节点名
    """
    user_message = state["messages"][-1]["content"]
    
    prompt = f"""
你是一个测试助手。判断用户想做什么，只输出以下选项之一，不要输出其他任何内容：

- generate_case: 用户想要生成测试用例
- run_api_test: 用户想要执行接口测试（涉及 API、接口、HTTP 请求）
- run_web_test: 用户想要执行 Web 自动化测试（涉及浏览器、网页、打开网站）
- chat: 普通对话，不属于以上任何情况

用户说：{user_message}

只输出一个选项：
"""
    
    try:
        response = llm.invoke(prompt)
        intent = response.content.strip().lower()
        
        # 判断逻辑：只要有对应关键词就触发对应工具，否则默认走 chat
        if "generate_case" in intent:
            state["next_step"] = "generate_case"
        elif "run_api_test" in intent or "api" in intent or "接口" in intent:
            state["next_step"] = "run_api_test"
        elif "run_web_test" in intent or "web" in intent or "浏览器" in intent:
            state["next_step"] = "run_web_test"
        else:
            state["next_step"] = "chat"
    except Exception as e:
        # 如果 LLM 调用失败，默认走普通聊天
        state["next_step"] = "chat"
    
    return state

# ---------- 节点2：生成测试用例 ----------
def generate_case(state: AgentState):
    """
    生成登录测试用例（示例）
    
    输入：用户消息
    输出：返回固定的测试用例步骤
    """
    state["messages"].append({
        "role": "assistant",
        "content": "📋 已生成登录测试用例：\n1. 打开登录页面\n2. 输入用户名\n3. 输入密码\n4. 点击登录按钮\n5. 验证登录成功"
    })
    state["next_step"] = "end"
    return state

# ---------- 节点3：执行接口测试 ----------
def run_api_test(state: AgentState):
    """
    执行真实的接口测试
    
    输入：用户消息（如 "测试 GET https://httpbin.org/get"）
    输出：状态码、响应时间、响应体预览
    
    关键步骤：
    1. 从用户消息中提取 URL 和 HTTP 方法
    2. 用 requests 库发送真实请求
    3. 捕获状态码、响应时间、响应体
    """
    user_message = state["messages"][-1]["content"]
    
    # 从用户消息中提取 URL
    parts = user_message.split()
    method = "GET"
    url = None
    
    for part in parts:
        if part.upper() in ["GET", "POST", "PUT", "DELETE"]:
            method = part.upper()
        elif part.startswith("http://") or part.startswith("https://"):
            url = part
    
    # 如果没有提取到 URL，提示用户
    if not url:
        state["messages"].append({
            "role": "assistant",
            "content": "⚠️ 请提供完整的测试信息，例如：\n'测试 GET https://api.example.com/users'\n'测试 POST https://api.example.com/login'"
        })
        state["next_step"] = "end"
        return state
    
    # 执行真实的 HTTP 请求
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, timeout=10)
        elif method == "PUT":
            response = requests.put(url, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        
        # 构建测试结果
        result = f"""
🧪 接口测试结果：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 URL: {url}
📌 方法: {method}
📊 状态码: {response.status_code}
✅ 状态: {'通过 ✅' if response.status_code < 400 else '失败 ❌'}
⏱️ 响应时间: {response.elapsed.total_seconds():.2f} 秒
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 响应体预览:
{response.text[:500]}
"""
        state["messages"].append({
            "role": "assistant",
            "content": result
        })
    except requests.exceptions.ConnectionError:
        state["messages"].append({
            "role": "assistant",
            "content": f"❌ 连接失败：无法访问 {url}，请检查网络或 URL 是否正确"
        })
    except requests.exceptions.Timeout:
        state["messages"].append({
            "role": "assistant",
            "content": f"❌ 请求超时：{url} 响应超过 10 秒"
        })
    except Exception as e:
        state["messages"].append({
            "role": "assistant",
            "content": f"❌ 测试失败：{str(e)}"
        })
    
    state["next_step"] = "end"
    return state

# ---------- 节点4：执行 Web 自动化测试 ----------
import time
import threading
from playwright.sync_api import sync_playwright

def run_web_test(state: AgentState):
    """执行 Web 自动化测试（通过子进程调用独立脚本）"""
    user_message = state["messages"][-1]["content"]
    
    # 提取 URL
    parts = user_message.split()
    url = None
    for part in parts:
        if part.startswith("http://") or part.startswith("https://"):
            url = part
            break
    
    if not url:
        state["messages"].append({
            "role": "assistant",
            "content": "⚠️ 请提供要测试的 URL，例如：\n'测试百度 https://www.baidu.com'"
        })
        state["next_step"] = "end"
        return state
    
    try:
        # 调用独立脚本
        result_str = subprocess.run(
            ["python", "app/run_web_test_script.py", url],
            capture_output=True,
            text=True,
            timeout=60
        ).stdout
        
        result = json.loads(result_str.strip())
        
        if result.get("error"):
            state["messages"].append({
                "role": "assistant",
                "content": f"❌ Web 测试失败：{result['error']}"
            })
        else:
            state["messages"].append({
                "role": "assistant",
                "content": f"""
🌐 Web 自动化测试结果：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 URL: {url}
📊 状态码: {result['status']}
📄 页面标题: {result['title']}
📸 截图已保存: {result['screenshot']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 测试完成
"""
            })
    except Exception as e:
        state["messages"].append({
            "role": "assistant",
            "content": f"❌ Web 测试失败：{str(e)}"
        })
    
    state["next_step"] = "end"
    return state

# ---------- 节点5：普通聊天 ----------
def chat(state: AgentState):
    """
    普通对话节点
    
    输入：用户最新消息
    输出：LLM 直接回复
    """
    user_message = state["messages"][-1]["content"]
    response = llm.invoke(user_message)
    state["messages"].append({
        "role": "assistant",
        "content": response.content
    })
    state["next_step"] = "end"
    return state

# ============================================
# 第4部分：构建图（Graph）
# ============================================
def build_agent():
    """
    构建 LangGraph 状态图
    
    流程：
    identify_intent → 根据意图选择节点 → 执行节点 → END
    """
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("identify_intent", identify_intent)
    workflow.add_node("generate_case", generate_case)
    workflow.add_node("run_api_test", run_api_test)
    workflow.add_node("run_web_test", run_web_test)
    workflow.add_node("chat", chat)
    
    # 入口节点
    workflow.set_entry_point("identify_intent")
    
    # 条件边：根据意图选择下一个节点
    workflow.add_conditional_edges(
        "identify_intent",
        lambda state: state["next_step"],
        {
            "generate_case": "generate_case",
            "run_api_test": "run_api_test",
            "run_web_test": "run_web_test",
            "chat": "chat",
            "end": END
        }
    )
    
    # 所有执行节点完成后都指向 END
    workflow.add_edge("generate_case", END)
    workflow.add_edge("run_api_test", END)
    workflow.add_edge("run_web_test", END)
    workflow.add_edge("chat", END)
    
    return workflow.compile()

# ============================================
# 第5部分：对外接口
# ============================================
agent = build_agent()

def run_agent(user_message: str) -> str:
    """
    运行 Agent，返回最终回答
    
    使用方式：
    result = run_agent("帮我生成一个登录测试用例")
    """
    initial_state = {
        "messages": [{"role": "user", "content": user_message}],
        "next_step": ""
    }
    result = agent.invoke(initial_state)
    
    # 返回最后一条 AI 消息
    for msg in reversed(result["messages"]):
        if msg["role"] == "assistant":
            return msg["content"]
    return "处理失败"