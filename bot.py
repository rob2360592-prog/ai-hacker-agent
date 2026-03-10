#!/usr/bin/env python3
"""
🤖 AI HACKER AGENT - Telegram Bot
=================================
Multi-AI Agent System with Telegram Interface
Free Forever - No Credit Card Required

Features:
- Multi-AI Discussion Mode (ChatGPT + DeepSeek + Groq)
- Ethical Hacking Assistant
- Code Generator & Debugger
- Research & Summarization
- Secure - User ID Protected

Author: AI Assistant
License: MIT
"""

import os
import json
import logging
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get from environment variables or use defaults for testing
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))

# AI API Keys - Free tiers available
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# API Endpoints
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AIResponse:
    """Structure for AI response"""
    provider: str
    model: str
    content: str
    response_time: float
    success: bool
    error: Optional[str] = None

@dataclass
class DiscussionResult:
    """Structure for multi-AI discussion"""
    original_question: str
    responses: List[AIResponse]
    final_summary: str
    timestamp: str

# ============================================================================
# AI AGENT CLASS
# ============================================================================

class AIAgent:
    """Multi-AI Agent Coordinator"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.models = {
            "openrouter": {
                "name": "ChatGPT-4o",
                "model": "openai/gpt-4o-mini",
                "available": bool(OPENROUTER_API_KEY)
            },
            "deepseek": {
                "name": "DeepSeek-V3",
                "model": "deepseek-chat",
                "available": bool(DEEPSEEK_API_KEY)
            },
            "groq": {
                "name": "Llama-3-Groq",
                "model": "llama-3.3-70b-versatile",
                "available": bool(GROQ_API_KEY)
            }
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_available_models(self) -> Dict:
        """Get list of available AI models"""
        return {k: v for k, v in self.models.items() if v["available"]}
    
    async def ask_openrouter(self, prompt: str, system_msg: str = "") -> AIResponse:
        """Query OpenRouter (ChatGPT)"""
        import time
        start_time = time.time()
        
        if not OPENROUTER_API_KEY:
            return AIResponse("openrouter", "gpt-4o-mini", "", 0, False, "API key not configured")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-hacker-agent.com",
            "X-Title": "AI Hacker Agent"
        }
        
        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            async with self.session.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return AIResponse("openrouter", "gpt-4o-mini", content, time.time() - start_time, True)
                else:
                    error_text = await resp.text()
                    return AIResponse("openrouter", "gpt-4o-mini", "", time.time() - start_time, False, error_text)
        except Exception as e:
            return AIResponse("openrouter", "gpt-4o-mini", "", time.time() - start_time, False, str(e))
    
    async def ask_deepseek(self, prompt: str, system_msg: str = "") -> AIResponse:
        """Query DeepSeek AI"""
        import time
        start_time = time.time()
        
        if not DEEPSEEK_API_KEY:
            return AIResponse("deepseek", "deepseek-chat", "", 0, False, "API key not configured")
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            async with self.session.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return AIResponse("deepseek", "deepseek-chat", content, time.time() - start_time, True)
                else:
                    error_text = await resp.text()
                    return AIResponse("deepseek", "deepseek-chat", "", time.time() - start_time, False, error_text)
        except Exception as e:
            return AIResponse("deepseek", "deepseek-chat", "", time.time() - start_time, False, str(e))
    
    async def ask_groq(self, prompt: str, system_msg: str = "") -> AIResponse:
        """Query Groq AI"""
        import time
        start_time = time.time()
        
        if not GROQ_API_KEY:
            return AIResponse("groq", "llama-3.3-70b", "", 0, False, "API key not configured")
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            async with self.session.post(GROQ_URL, headers=headers, json=payload, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return AIResponse("groq", "llama-3.3-70b", content, time.time() - start_time, True)
                else:
                    error_text = await resp.text()
                    return AIResponse("groq", "llama-3.3-70b", "", time.time() - start_time, False, error_text)
        except Exception as e:
            return AIResponse("groq", "llama-3.3-70b", "", time.time() - start_time, False, str(e))
    
    async def multi_ai_discussion(self, prompt: str, mode: str = "general") -> DiscussionResult:
        """
        Run a discussion between multiple AI agents
        
        Mode options:
        - general: General discussion
        - hacking: Ethical hacking mode
        - coding: Programming mode
        - research: Research mode
        """
        # System messages for different modes
        system_messages = {
            "general": "You are a helpful AI assistant. Provide clear and concise answers.",
            "hacking": """You are an ethical hacking expert. You help with:
- Security assessments and vulnerability analysis
- Penetration testing methodologies
- Network scanning techniques
- Security tool recommendations
- Educational security concepts

Always emphasize ethical use and legal compliance. Never provide instructions for illegal activities.""",
            "coding": "You are an expert programmer. Write clean, well-documented code with explanations.",
            "research": "You are a research assistant. Provide comprehensive, well-structured information with sources when possible."
        }
        
        system_msg = system_messages.get(mode, system_messages["general"])
        
        # Query all available AIs concurrently
        tasks = []
        available = self.get_available_models()
        
        if "openrouter" in available:
            tasks.append(self.ask_openrouter(prompt, system_msg))
        if "deepseek" in available:
            tasks.append(self.ask_deepseek(prompt, system_msg))
        if "groq" in available:
            tasks.append(self.ask_groq(prompt, system_msg))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_responses = []
        for r in responses:
            if isinstance(r, Exception):
                logger.error(f"AI query failed: {r}")
            else:
                valid_responses.append(r)
        
        # Generate summary from successful responses
        successful = [r for r in valid_responses if r.success]
        
        if not successful:
            summary = "❌ جميع نماذج AI غير متاحة حالياً. يرجى التحقق من إعدادات API."
        elif len(successful) == 1:
            summary = successful[0].content
        else:
            # Create a summary combining all responses
            summary_parts = ["🧠 **ملخص المحكمة الذكية**\n"]
            summary_parts.append(f"تم الاستعانة بـ {len(successful)} نماذج AI\n")
            summary_parts.append("═" * 40 + "\n")
            
            for resp in successful:
                emoji = {"openrouter": "🟢", "deepseek": "🔵", "groq": "🟣"}.get(resp.provider, "⚪")
                summary_parts.append(f"\n{emoji} **{resp.provider.upper()}** ({resp.response_time:.1f}s):")
                summary_parts.append(f"{resp.content[:500]}...\n" if len(resp.content) > 500 else f"{resp.content}\n")
            
            summary = "\n".join(summary_parts)
        
        return DiscussionResult(
            original_question=prompt,
            responses=valid_responses,
            final_summary=summary,
            timestamp=datetime.now().isoformat()
        )

# ============================================================================
# SECURITY FUNCTIONS
# ============================================================================

def is_authorized(user_id: int) -> bool:
    """Check if user is authorized"""
    if AUTHORIZED_USER_ID == 0:
        # In development mode, allow all
        return True
    return user_id == AUTHORIZED_USER_ID

# ============================================================================
# BOT COMMAND HANDLERS
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    if not is_authorized(user.id):
        await update.message.reply_text(
            "🚫 **غير مصرح**\n"
            "عذراً، ليس لديك صلاحية الوصول لهذا البوت.\n"
            f"معرف المستخدم الخاص بك: `{user.id}`",
            parse_mode='Markdown'
        )
        return
    
    welcome_message = f"""
🤖 **مرحباً بك في AI Hacker Agent!**

أهلاً {user.first_name}! أنا بوت متعدد الذكاء الاصطناعي، أستطيع:

🧠 **الأوامر المتاحة:**
/start - عرض هذه الرسالة
/help - عرض المساعدة التفصيلية
/chat [سؤال] - محادثة مع AI
/multi [سؤال] - وضع المحكمة (متعدد AI)
/hack [هدف] - وضع الهاكر الأخلاقي
/code [طلب] - وضع المبرمج
/search [موضوع] - البحث والتلخيص
/status - حالة النظام

⚡ **مميزاتي:**
• دمج متعدد نماذج AI (ChatGPT + DeepSeek + Groq)
• وضع الهاكر الأخلاقي للاختبار الأمني
• كتابة وتحليل الأكواد
• مجاني 100% - لا يحتاج بطاقة ائتمان

📝 **مثال:**
`/multi اشرح لي كيفية تأمين موقع WordPress`

ابدأ الآن! 🚀
"""
    
    keyboard = [
        [InlineKeyboardButton("🧠 وضع المحكمة", callback_data='mode_multi')],
        [InlineKeyboardButton("🔒 وضع الهاكر", callback_data='mode_hack')],
        [InlineKeyboardButton("💻 وضع المبرمج", callback_data='mode_code')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    if not is_authorized(update.effective_user.id):
        return
    
    help_text = """
📚 **دليل استخدام AI Hacker Agent**

**الأوامر الأساسية:**
• `/chat [سؤال]` - محادثة عادية مع AI
• `/multi [سؤال]` - تفعيل وضع المحكمة (جميع AI يتناقشون)
• `/hack [هدف]` - وضع الهاكر الأخلاقي
• `/code [طلب]` - وضع المبرمج
• `/search [موضوع]` - البحث والتلخيص
• `/status` - حالة النظام

**أمثلة:**

🧠 `/multi ما هي أفضل ممارسات أمان تطبيقات الويب؟`

🔒 `/hack كيف يمكنني فحص موقعي للثغرات الأمنية؟`

💻 `/code اكتب لي دالة Python لفحص منفذ مفتوح`

🔍 `/search ما هو الـ SQL Injection وكيف أتجنبه؟`

**ملاحظات:**
• جميع الخدمات مجانية 100%
• يدعم العربية والإنجليزية
• الردود قد تستغرق 10-30 ثانية
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /chat command"""
    if not is_authorized(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ **استخدام خاطئ**\n"
            "الصيغة: `/chat [سؤالك]`\n"
            "مثال: `/chat ما هو الـ XSS؟"`,
            parse_mode='Markdown'
        )
        return
    
    prompt = " ".join(context.args)
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action='typing'
    )
    
    async with AIAgent() as agent:
        result = await agent.multi_ai_discussion(prompt, mode="general")
    
    await update.message.reply_text(result.final_summary, parse_mode='Markdown')

async def multi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /multi command - Multi-AI discussion mode"""
    if not is_authorized(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ **استخدام خاطئ**\n"
            "الصيغة: `/multi [سؤالك]`\n"
            "مثال: `/multi ناقش أفضل طرق حماية قواعد البيانات`",
            parse_mode='Markdown'
        )
        return
    
    prompt = " ".join(context.args)
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action='typing'
    )
    
    # Send initial message
    msg = await update.message.reply_text(
        "🧠 **جاري تفعيل محكمة AI...**\n"
        "يتم الاستعانة بنماذج متعددة للحصول على أفضل إجابة...",
        parse_mode='Markdown'
    )
    
    async with AIAgent() as agent:
        result = await agent.multi_ai_discussion(prompt, mode="general")
    
    # Edit message with result
    await msg.edit_text(result.final_summary, parse_mode='Markdown')

async def hack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hack command - Ethical hacking mode"""
    if not is_authorized(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ **استخدام خاطئ**\n"
            "الصيغة: `/hack [هدف/سؤال]`\n"
            "مثال: `/hack كيف يمكنني تأمين موقعي ضد XSS؟`\n\n"
            "⚠️ **تنبيه:** هذا البوت للأغراض التعليمية والأخلاقية فقط!",
            parse_mode='Markdown'
        )
        return
    
    prompt = " ".join(context.args)
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action='typing'
    )
    
    msg = await update.message.reply_text(
        "🔒 **وضع الهاكر الأخلاقي...**\n"
        "جاري تحليل طلبك من منظور أمني...",
        parse_mode='Markdown'
    )
    
    async with AIAgent() as agent:
        result = await agent.multi_ai_discussion(prompt, mode="hacking")
    
    # Add ethical disclaimer
    response = result.final_summary + "\n\n" + "═" * 40 + "\n⚠️ **تنبيه أخلاقي:**\nهذه المعلومات للأغراض التعليمية فقط. استخدمها بمسؤولية وفي إطار القانون."
    
    await msg.edit_text(response, parse_mode='Markdown')

async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /code command - Programming mode"""
    if not is_authorized(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ **استخدام خاطئ**\n"
            "الصيغة: `/code [طلبك]`\n"
            "مثال: `/code اكتب لي سكريبت Python لفحص المنافذ المفتوحة`",
            parse_mode='Markdown'
        )
        return
    
    prompt = " ".join(context.args)
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action='typing'
    )
    
    msg = await update.message.reply_text(
        "💻 **وضع المبرمج...**\n"
        "جاري كتابة الكود...",
        parse_mode='Markdown'
    )
    
    async with AIAgent() as agent:
        result = await agent.multi_ai_discussion(prompt, mode="coding")
    
    await msg.edit_text(result.final_summary, parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command - Research mode"""
    if not is_authorized(update.effective_user.id):
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ **استخدام خاطئ**\n"
            "الصيغة: `/search [موضوع]`\n"
            "مثال: `/search ما هو الـ Zero Day Exploit؟`",
            parse_mode='Markdown'
        )
        return
    
    prompt = " ".join(context.args)
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action='typing'
    )
    
    msg = await update.message.reply_text(
        "🔍 **جاري البحث...**\n"
        "يتم جمع المعلومات من مصادر متعددة...",
        parse_mode='Markdown'
    )
    
    async with AIAgent() as agent:
        result = await agent.multi_ai_discussion(prompt, mode="research")
    
    await msg.edit_text(result.final_summary, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    if not is_authorized(update.effective_user.id):
        return
    
    async with AIAgent() as agent:
        available = agent.get_available_models()
    
    status_text = "📊 **حالة النظام**\n\n"
    status_text += "🤖 **نماذج AI المتاحة:**\n"
    
    for provider, info in available.items():
        emoji = "🟢" if info["available"] else "🔴"
        status_text += f"{emoji} **{info['name']}** ({provider})\n"
    
    if not available:
        status_text += "🔴 لا توجد نماذج متاحة - تحقق من إعدادات API\n"
    
    status_text += f"\n👤 **المستخدم المصرح:** `{AUTHORIZED_USER_ID if AUTHORIZED_USER_ID else 'الكل (وضع التطوير)'}`"
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if not is_authorized(update.effective_user.id):
        return
    
    if query.data == 'mode_multi':
        await query.edit_message_text(
            "🧠 **وضع المحكمة**\n\n"
            "في هذا الوضع، يتم الاستعانة بـ 3 نماذج AI مختلفة:\n"
            "• ChatGPT-4o (OpenRouter)\n"
            "• DeepSeek-V3\n"
            "• Llama-3.3 (Groq)\n\n"
            "كل نموذج يعطي رأيه، ثم يتم تقديم ملخص شامل.\n\n"
            "**الاستخدام:** `/multi [سؤالك]`",
            parse_mode='Markdown'
        )
    elif query.data == 'mode_hack':
        await query.edit_message_text(
            "🔒 **وضع الهاكر الأخلاقي**\n\n"
            "هذا الوضع متخصص في:\n"
            "• تقييم الثغرات الأمنية\n"
            "• اختبار الاختراق\n"
            "• تحليل الشبكات\n"
            "• تأمين الأنظمة\n\n"
            "⚠️ للأغراض التعليمية فقط!\n\n"
            "**الاستخدام:** `/hack [سؤالك]`",
            parse_mode='Markdown'
        )
    elif query.data == 'mode_code':
        await query.edit_message_text(
            "💻 **وضع المبرمج**\n\n"
            "هذا الوضع متخصص في:\n"
            "• كتابة الأكواد\n"
            "• تصحيح الأخطاء\n"
            "• شرح الكود\n"
            "• تحويل الأكواد بين اللغات\n\n"
            "يدعم: Python, JavaScript, Bash, SQL, وأكثر\n\n"
            "**الاستخدام:** `/code [طلبك]`",
            parse_mode='Markdown'
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    if not is_authorized(update.effective_user.id):
        return
    
    # If message starts with /, it's a command - ignore
    if update.message.text.startswith('/'):
        return
    
    # Treat as /chat command
    prompt = update.message.text
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action='typing'
    )
    
    async with AIAgent() as agent:
        result = await agent.multi_ai_discussion(prompt, mode="general")
    
    await update.message.reply_text(result.final_summary, parse_mode='Markdown')

# ============================================================================
# ERROR HANDLER
# ============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ **حدث خطأ**\n"
            "عذراً، حدث خطأ أثناء معالجة طلبك.\n"
            "يرجى المحاولة مرة أخرى.",
            parse_mode='Markdown'
        )

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Start the bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        print("❌ خطأ: TELEGRAM_BOT_TOKEN غير محدد!")
        print("يرجى تعيين متغير البيئة TELEGRAM_BOT_TOKEN")
        return
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("chat", chat_command))
    application.add_handler(CommandHandler("multi", multi_command))
    application.add_handler(CommandHandler("hack", hack_command))
    application.add_handler(CommandHandler("code", code_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting AI Hacker Agent Bot...")
    print("🤖 AI Hacker Agent Bot يعمل الآن!")
    print("اضغط Ctrl+C للإيقاف")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
