import random
import discord
from discord.ext import commands
from buffs import BUFFS
from debuffs import DEBUFFS
import re
import copy
from data_default import DEFAULT_USER

VALID_ATTRIBUTES = {"CON", "FOR", "INT", "DEX", "PRE", "CAR"}

DIFFICULTY = {
    0: 18,
    1: 14,
    2: 11,
    3: 7,
    4: 3
}

class rollManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll", aliases=["rolar", "dado", "diceroll"])
    async def roll(self, ctx, attribute: str, perk: int = 0, member: discord.Member = None):

        # --- Target ---
        member = member or ctx.author
        user_id = str(member.id)

        # --- Ensure data exists ---
        if user_id not in self.bot.user_data:
            self.bot.user_data[user_id] = copy.deepcopy(DEFAULT_USER)
            self.bot.save_data()

        data = self.bot.user_data[user_id]

        # --- Validate attribute ---
        attribute = attribute.upper()
        if attribute not in VALID_ATTRIBUTES:
            await ctx.send(f"❌ Invalid attribute. Use: {', '.join(VALID_ATTRIBUTES)}")
            return

        # --- 1. Raw d20 roll ---
        raw_roll = random.randint(1, 20)
        total = raw_roll
        breakdown = []

        # --- 2. Attribute points (DIFFICULTY ONLY) ---
        base_attr = data["attributes"].get(attribute, 0)

        # =========================
        # BUFFS
        # =========================
        expired_buffs = []

        for buff_entry in data.get("buffs", []):
            buff = BUFFS[buff_entry["id"]]

            for attr, value in buff["effects"].items():
                if attr == attribute:
                    total += value
                    breakdown.append(f"{buff['name']} ({attr}): {value:+}")

                elif attr == "HP":
                    data["health"] -= abs(value)
                    breakdown.append(f"{buff['name']}: {-abs(value)} HP")

                elif attr == "SAN":
                    data["sanity"] -= abs(value)
                    breakdown.append(f"{buff['name']}: {-abs(value)} SAN")

            # Consume roll if temporary
            if buff_entry["rolls"] is not None:
                buff_entry["rolls"] -= 1
                if buff_entry["rolls"] <= 0:
                    expired_buffs.append(buff_entry)

        for buff in expired_buffs:
            data["buffs"].remove(buff)

        # =========================
        # DEBUFFS
        # =========================
        expired_debuffs = []

        for debuff_entry in data.get("debuffs", []):
            debuff = DEBUFFS[debuff_entry["id"]]

            for attr, value in debuff["effects"].items():
                if attr == attribute:
                    total += value
                    breakdown.append(f"{debuff['name']} ({attr}): {value:+}")

                elif attr == "HP":
                    data["health"] -= abs(value)
                    breakdown.append(f"{debuff['name']}: {-abs(value)} HP")

                elif attr == "SAN":
                    data["sanity"] -= abs(value)
                    breakdown.append(f"{debuff['name']}: {-abs(value)} SAN")

            if debuff_entry["rolls"] is not None:
                debuff_entry["rolls"] -= 1
                if debuff_entry["rolls"] <= 0:
                    expired_debuffs.append(debuff_entry)

        for debuff in expired_debuffs:
            data["debuffs"].remove(debuff)

        # =========================
        # MODIFIERS (PERMANENT)
        # =========================
        for mod in data.get("modifiers", []):
            if attribute in mod["effects"]:
                value = mod["effects"][attribute]
                total += value
                breakdown.append(f"{mod['name']}: {value:+}")

        # =========================
        # BOOST (CONSUMED)
        # =========================
        boost = data.get("boost", 0)
        if boost:
            total += boost
            breakdown.append(f"Boost: {boost:+}")
            data["boost"] = 0

        # =========================
        # PERK
        # =========================
        if perk:
            total += perk
            breakdown.append(f"Perícia: {perk:+}")

        # =========================
        # Clamp HP / SAN
        # =========================
        data["health"] = max(0, min(data["health"], data["maxhealth"]))
        data["sanity"] = max(0, min(data["sanity"], data["maxsanity"]))

        # =========================
        # Difficulty Check
        # =========================
        attr_points = min(base_attr, 4)
        difficulty = DIFFICULTY[attr_points]
        success = total >= difficulty

        # --- Save ---
        self.bot.save_data()

        # =========================
        # Output
        # =========================

        # =========================
        # Critical check (FINAL TOTAL)
        # =========================
        critical = None

        if total <= 1:
            critical = "failure"
        elif total >= 20:
            critical = "success"

        if critical == "success":
            result = "🌟 **MÁXIMO NATURAL!**"
            color = discord.Color.gold()
        elif critical == "failure":
            result = "💀 **FALHA CRÍTICA!**"
            color = discord.Color.dark_red()
        else:
            color = discord.Color.green() if success else discord.Color.red()
            result = "✅ **SUCESSO**" if success else "❌ **FALHA**"

        breakdown_text = (
            "```diff\n" + "\n".join(breakdown) + "\n```"
            if breakdown else ""
        )

        embed = discord.Embed(
            title=result,
            color=color
        )

        embed.add_field(
            name="🎯 Dificuldade",
            value=str(difficulty),
            inline=True
        )

        embed.add_field(
            name="🎲 Resultado d20",
            value=str(raw_roll),
            inline=True
        )

        embed.add_field(
            name="📊 Resultado Final",
            value=str(total),
            inline=True
        )

        # Only show breakdown if it exists
        if breakdown:
            embed.add_field(
                name="📌 Modificadores",
                value="```diff\n" + "\n".join(breakdown) + "\n```",
                inline=False
            )

        embed.set_footer(text=f"Rolagem de {ctx.author.display_name}")

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower().replace(" ", "")

        match = re.fullmatch(r"\.(\d*)d(\d+)([+-]\d+)?", content)
        if not match:
            return

        amount = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        if amount < 1 or sides < 2:
            await message.channel.send("❌ Invalid dice values.")
            return

        if amount > 100:
            await message.channel.send("❌ Too many dice.")
            return

        rolls = [random.randint(1, sides) for _ in range(amount)]
        modified_rolls = [r + modifier for r in rolls]

        total = sum(modified_rolls)

        modifier_text = f"{modifier:+d}" if modifier else ""

        rolls_text = ", ".join(
            f"{r}{modifier_text}" if modifier else str(r)
            for r in rolls
        )

        await message.channel.send(
            f"🎲 **Rolagem:** `{amount}d{sides}{modifier_text}`\n"
            f"- Resultados: [{rolls_text}]\n"
            f"- Total: **{total}**"
        )

async def setup(bot):
    await bot.add_cog(rollManager(bot))