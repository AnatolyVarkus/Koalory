from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UsersModel, StoriesModel, PaymentsModel
from datetime import datetime, timedelta

async def gather_analytics(session: AsyncSession) -> str:
    now = datetime.utcnow()
    one_day_ago = now - timedelta(days=1)
    one_week_ago = now - timedelta(weeks=1)

    # USERS
    new_users_day = await session.scalar(
        select(func.count()).where(UsersModel.created_at >= one_day_ago)
    )
    new_users_week = await session.scalar(
        select(func.count()).where(UsersModel.created_at >= one_week_ago)
    )
    total_users = await session.scalar(select(func.count()).select_from(UsersModel))
    verified_users = await session.scalar(
        select(func.count()).where(UsersModel.verified.is_(True))
    )

    # STORIES
    completed_stories = await session.scalar(
        select(func.count()).where(StoriesModel.status == "completed")
    )
    avg_stories_per_user = (
        completed_stories / total_users if total_users else 0
    )

    # PAYMENTS
    total_payments = await session.scalar(select(func.count()).select_from(PaymentsModel.amount_in_cents))
    total_paid_users = await session.scalar(
        select(func.count(func.distinct(PaymentsModel.user_id)))
    )
    avg_payments_per_user = (
        total_payments / total_paid_users if total_paid_users else 0
    )
    total_payment_sum = await session.scalar(
        select(func.sum(PaymentsModel.available_stories))
    )

    return f"""
📊 <b>Analytics Report</b>

👤 <b>Users</b>
• New (24h): {new_users_day}
• New (7d): {new_users_week}
• Total: {total_users}
• Verified: {verified_users}

📖 <b>Stories</b>
• Completed: {completed_stories}
• Avg. per user: {avg_stories_per_user:.2f}

💰 <b>Payments</b>
• Total payments: ${total_payments/100:.2f}
• Unique payers: {total_paid_users}
• Avg. per payer: ${avg_payments_per_user/100:.2f}
• Total story credits sold: {total_payment_sum or 0}
""".strip()