from discord.ext import commands
import discord
from buffs import BUFFS
from debuffs import DEBUFFS

class BuffHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="applybuff", aliases=["addbuff", "buff"])
    @commands.has_permissions(manage_guild=True)
    async def applybuff(self, ctx, member: discord.Member, buff: str, rolls: int = None):
        buff = buff.lower()

        if buff not in BUFFS:
            await ctx.send("❌ Invalid buff.")
            return

        if rolls is not None and rolls < 1:
            await ctx.send("❌ Rolls must be at least 1.")
            return

        user_id = str(member.id)

        if user_id not in self.bot.user_data:
            self.bot.user_data[user_id] = copy.deepcopy(DEFAULT_USER)

        buffs = self.bot.user_data[user_id]["buffs"]

        if any(b["id"] == buff for b in buffs):
            await ctx.send(f"❌ {member.name} already has this buff.")
            return

        buffs.append({
            "id": buff,
            "rolls": rolls  # None = infinite
        })

        self.bot.save_data()

        duration_text = "∞ (indefinite)" if rolls is None else f"{rolls} rolls"

        buff_data = BUFFS[buff]
        await ctx.send(
            f"{buff_data['emoji']} **{buff_data['name']}** applied to {member.mention}\n"
            f"⏳ Duration: **{duration_text}**"
        )

    @commands.command(name="applydebuff", aliases=["adddebuff", "debuff"])
    @commands.has_permissions(manage_guild=True)
    async def applydebuff(self, ctx, member: discord.Member, debuff: str, rolls: int = None):
        debuff = debuff.lower()

        if debuff not in DEBUFFS:
            await ctx.send("❌ Invalid debuff.")
            return

        if rolls is not None and rolls < 1:
            await ctx.send("❌ Rolls must be at least 1.")
            return

        user_id = str(member.id)

        if user_id not in self.bot.user_data:
            self.bot.user_data[user_id] = copy.deepcopy(DEFAULT_USER)

        debuffs = self.bot.user_data[user_id]["debuffs"]

        if any(d["id"] == debuff for d in debuffs):
            await ctx.send(f"❌ {member.name} already has this debuff.")
            return

        debuffs.append({
            "id": debuff,
            "rolls": rolls
        })

        self.bot.save_data()

        duration_text = "∞ (indefinite)" if rolls is None else f"{rolls} rolls"

        debuff_data = DEBUFFS[debuff]
        await ctx.send(
            f"{debuff_data['emoji']} **{debuff_data['name']}** applied to {member.mention}\n"
            f"⏳ Duration: **{duration_text}**"
        )

    @commands.command(name="removebuff")
    async def removebuff(self, ctx, member: discord.Member, *, buff_name: str):
        user_id = str(member.id)

        if user_id not in self.bot.user_data:
            await ctx.send("❌ User has no data.")
            return

        data = self.bot.user_data[user_id]
        buffs = data.get("buffs", [])

        target = buff_name.lower()

        removed = False
        new_buffs = []

        for buff in buffs:
            # Handle dict-based old data
            if isinstance(buff, dict):
                buff_id = buff.get("id") or buff.get("name", "").lower()
            else:
                buff_id = str(buff).lower()

            if buff_id == target:
                removed = True
                continue

            new_buffs.append(buff)

        if not removed:
            await ctx.send("❌ User does not have that buff.")
            return

        data["buffs"] = new_buffs
        self.bot.save_data()

        await ctx.send(f"✅ Removed buff **{buff_name}** from {member.mention}.")

    @commands.command(name="removedebuff")
    async def removedebuff(self, ctx, member: discord.Member, *, debuff_name: str):
        user_id = str(member.id)

        if user_id not in self.bot.user_data:
            await ctx.send("❌ User has no data.")
            return

        data = self.bot.user_data[user_id]
        debuffs = data.get("debuffs", [])

        target = debuff_name.lower()

        removed = False
        new_debuffs = []

        for debuff in debuffs:
            if isinstance(debuff, dict):
                debuff_id = debuff.get("id") or debuff.get("name", "").lower()
            else:
                debuff_id = str(debuff).lower()

            if debuff_id == target:
                removed = True
                continue

            new_debuffs.append(debuff)

        if not removed:
            await ctx.send("❌ User does not have that debuff.")
            return

        data["debuffs"] = new_debuffs
        self.bot.save_data()

        await ctx.send(f"✅ Removed debuff **{debuff_name}** from {member.mention}.")

    @commands.command(name="clearbuffs", aliases=["removeallbuffs", "wipebuffs"])
    @commands.has_permissions(manage_guild=True)
    async def clearbuffs(self, ctx, member: discord.Member):
        user_id = str(member.id)

        if user_id not in self.bot.user_data:
            await ctx.send("❌ User has no data.")
            return

        data = self.bot.user_data[user_id]
        buffs = data.get("buffs", [])

        if not buffs:
            await ctx.send(f"ℹ️ {member.name} has no buffs.")
            return

        # Hard reset (safe for any format)
        data["buffs"] = []
        self.bot.save_data()

        await ctx.send(f"🧹 All buffs cleared from {member.mention}.")

    @commands.command(name="cleardebuffs", aliases=["removealldebuffs", "wipedebuffs"])
    @commands.has_permissions(manage_guild=True)
    async def cleardebuffs(self, ctx, member: discord.Member):
        user_id = str(member.id)

        if user_id not in self.bot.user_data:
            await ctx.send("❌ User has no data.")
            return

        data = self.bot.user_data[user_id]
        debuffs = data.get("debuffs", [])

        if not debuffs:
            await ctx.send(f"ℹ️ {member.name} has no debuffs.")
            return

        # Hard reset (safe for any format)
        data["debuffs"] = []
        self.bot.save_data()

        await ctx.send(f"🧹 All debuffs cleared from {member.mention}.")


async def setup(bot):
    await bot.add_cog(BuffHandler(bot))