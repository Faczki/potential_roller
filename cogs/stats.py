import discord
from discord.ext import commands
from buffs import BUFFS
from data_default import DEFAULT_USER
import copy
from debuffs import DEBUFFS

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_inventory_weight(self, user_id):
        items = self.bot.user_data[user_id].get("items", {})
        return sum(
            item["amount"] * item["weight"]
            for item in items.values()
        )

    @commands.command(aliases=["seestats", "sheet", "profile", "character"])
    async def stats(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_id = str(member.id)

        # Ensure user data exists
        if user_id not in self.bot.user_data:
            self.bot.user_data[user_id] = copy.deepcopy(DEFAULT_USER)
            self.bot.save_data()

        data = self.bot.user_data[user_id]

        # ─────────────────────────────
        # Helpers
        # ─────────────────────────────
        def normalize_effect_list(raw):
            if not raw:
                return []

            if isinstance(raw, dict):
                return list(raw.keys())

            if isinstance(raw, list):
                result = []
                for item in raw:
                    if isinstance(item, str):
                        result.append(item)
                    elif isinstance(item, dict) and "name" in item:
                        result.append(item["name"])
                return result

            return []

        # ─────────────────────────────
        # Basic stats
        # ─────────────────────────────
        health = data["health"]
        maxhealth = data["maxhealth"]
        sanity = data["sanity"]
        maxsanity = data["maxsanity"]
        boost = data["boost"]
        level = data["level"]

        attrs = data["attributes"]
        CON = attrs["CON"]
        FOR = attrs["FOR"]
        INT = attrs["INT"]
        DEX = attrs["DEX"]
        PRE = attrs["PRE"]
        CAR = attrs["CAR"]

        # ─────────────────────────────
        # Health & sanity emojis
        # ─────────────────────────────
        healthPercentage = (health / maxhealth) * 100
        sanPercentage = (sanity / maxsanity) * 100

        if healthPercentage >= 90:
            emoji = "<:heart0:1457790339145400493>"
        elif healthPercentage >= 60:
            emoji = "<:heart1:1457790393583403250>"
        elif healthPercentage >= 40:
            emoji = "<:heart2:1457790449983946948>"
        elif healthPercentage >= 20:
            emoji = "<:heart3:1457790527394156709>"
        else:
            emoji = "<:heart4:1457790583870455939>"

        if sanPercentage >= 90:
            sanEmoji = "<:san1:1455953778191630349>"
        elif sanPercentage >= 60:
            sanEmoji = "<:san2:1455957180237877339>"
        elif sanPercentage >= 40:
            sanEmoji = "<:san3:1455955144280768545>"
        elif sanPercentage >= 20:
            sanEmoji = "<:san4:1455957540717330644>"
        else:
            sanEmoji = "<:san5:1455956905758429370>"

        # ─────────────────────────────
        # Buffs & Debuffs (SAFE)
        # ─────────────────────────────
        buff_keys = data.get("buffs", [])
        debuff_keys = data.get("debuffs", [])

        buff_emojis = []
        for buff_key in buff_keys:
            if isinstance(buff_key, dict):
                buff_key = buff_key.get("id") or buff_key.get("name")

            buff_key = str(buff_key).lower()

            if buff_key in BUFFS:
                emoji = BUFFS[buff_key].get("emoji")
                if emoji:
                    buff_emojis.append(emoji)

        buffs_display = " ".join(buff_emojis) if buff_emojis else "Nenhum"

        debuff_emojis = []
        for debuff_key in debuff_keys:
            if isinstance(debuff_key, dict):
                debuff_key = debuff_key.get("id") or debuff_key.get("name")

            debuff_key = str(debuff_key).lower()

            if debuff_key in DEBUFFS:
                emoji = DEBUFFS[debuff_key].get("emoji")
                if emoji:
                    debuff_emojis.append(emoji)

        debuffs_display = " ".join(debuff_emojis) if debuff_emojis else "Nenhum"

        # ─────────────────────────────
        # Modifiers
        # ─────────────────────────────
        modifiers = data.get("modifiers", [])

        if modifiers:
            modifier_lines = []
            for mod in modifiers:
                name = mod.get("name", "Unnamed Modifier")
                effects = mod.get("effects", {})

                effects_text = "".join(
                    f"\n>    └ {attr} ({value:+d})"
                    for attr, value in effects.items()
                )

                modifier_lines.append(f"{name}{effects_text}")

            modifiers_display = "\n > ".join(modifier_lines)
        else:
            modifiers_display = "Nenhum"

        # ─────────────────────────────
        # Embed
        # ─────────────────────────────
        embed = discord.Embed(
            title=f"Perfil de {member.name} (Nível {level})",
            color=discord.Color.brand_green()
        )

        embed.add_field(
            name=f"{emoji} **HP**",
            value=f"**[{health}/{maxhealth}]**",
            inline=True
        )

        embed.add_field(
            name=f"{sanEmoji} **Sanidade**",
            value=f"**[{sanity}/{maxsanity}]**",
            inline=True
        )

        embed.add_field(
            name="<:buff:1456995409627975721> `Buffs`",
            value=buffs_display,
            inline=False
        )

        embed.add_field(
            name="<:debuff:1456995486912217192> `Debuffs`",
            value=debuffs_display,
            inline=False
        )

        embed.add_field(
            name="<:boost:1457789860105687143> `Boost`",
            value=str(boost),
            inline=True
        )

        embed.add_field(
            name="<:modifier:1457789634523300023> `Modificadores`",
            value=modifiers_display,
            inline=False
        )

        embed.add_field(
            name="⚜️ `Atributos`",
            value=(
                f"> **CON:** {CON}\n"
                f"> **FOR:** {FOR}\n"
                f"> **INT:** {INT}\n"
                f"> **DEX:** {DEX}\n"
                f"> **PRE:** {PRE}\n"
                f"> **CAR:** {CAR}"
            ),
            inline=False
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="inventory", aliases=["inv", "bag"])
    async def inventory(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_id = str(member.id)

        if user_id not in self.bot.user_data:
            self.bot.user_data[user_id] = copy.deepcopy(DEFAULT_USER)
            self.bot.save_data()

        data = self.bot.user_data[user_id]

        # --- Basic info ---
        cash = data.get("cash", 0)
        weapon = data.get("weapon") or "None"
        secondary = data.get("secondary") or "None"
        equipments = data.get("equipments", [])
        items = data.get("items", {})
        level = data.get("level", 0)

        # --- Armory ---
        armory = data.get("armory", {})
        armor = armory.get("armor", {})
        head = armor.get("head") or "None"
        chest = armor.get("chest") or "None"
        boots = armor.get("boots") or "None"
        hands = armor.get("hands") or "None"

        headEmoji = "<:headgear:1457035854898921492>"
        chestEmoji = "<:chestplate:1457035954568298569>"
        gloveEmoji = "<:gloves:1457036356705587252>"
        bootEmoji = "<:boots:1457036272639021191>"

        if head == "Nenhum":
            headEmoji = "<:noheadgear:1457042208866701627>"
        if chest == "Nenhum":
            chestEmoji = "<:nochestplate:1457042170799194213>"
        if hands == "Nenhum":
            gloveEmoji = "<:nogloves:1457042129434972347>"
        if boots == "Nenhum":
            bootEmoji = "<:noboots:1457042142240313476>"

        current_weight = self.get_inventory_weight(user_id)
        max_weight = data.get("inventory_space", 0)

        # --- Format equipments ---
        equipments_display = ", ".join(equipments) if equipments else "None"

        # --- Format items ---
        if items:
            item_lines = []
            for name, item in items.items():
                line = f"x{item['amount']} {name} ({item['weight']})"
                if item.get("description"):
                    line += f"\n  └ {item['description']}"
                item_lines.append(line)

            items_display = "\n".join(item_lines)
        else:
            items_display = "Vazio"

        embed = discord.Embed(
            title=f"Inventário de {member.name} (Nível {level})",
            color=discord.Color.gold()
        )

        embed.add_field(
            name="💰 `Monetário`",
            value= f"- **<:est_pra:1458505000291405898> Estrelas de Prata:** ${str(cash)}",
            inline=False
        )

        embed.add_field(
            name="🛡️ `Arsenal`",
            value=(
                f"- {headEmoji} **Cabeça:** {head}\n"
                f"- {chestEmoji} **Peitoral:** {chest}\n"
                f"- {gloveEmoji} **Mãos:** {hands}\n"
                f"- {bootEmoji} **Botas:** {boots}"
            ),
            inline=False
        )

        embed.add_field(
            name="⚔️ `Armas`",
            value=(
                f"- 🗡️  **Principal:** {weapon}\n"
                f"- <:pistol:1457037006767915181> **Secundária:** {secondary}"
            ),
            inline=False
        )

        embed.add_field(
            name="📦 `Equipamentos`",
            value= f"- {equipments_display}",
            inline=False
        )

        embed.add_field(
            name=f"⚖️ `Itens` [{current_weight}/{max_weight}]",
            value= f"```{items_display}```" if items_display != "Vazio" else "Nenhum item",
            inline=False
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))