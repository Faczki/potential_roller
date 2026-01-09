import discord
from discord.ext import commands
import copy
from data_default import DEFAULT_USER

VALID_ATTRIBUTES = {"CON", "FOR", "INT", "DEX", "PRE", "CAR"}

class AttributesHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Utility ---
    def ensure_user(self, user_id):
        if user_id not in self.bot.user_data:
            self.bot.user_data[user_id] = copy.deepcopy(DEFAULT_USER)

    # --- changeHealth ---
    @commands.command(name="changehealth", aliases=["sethealth", "hp", "health", "sethp"])
    @commands.has_permissions(manage_guild=True)
    async def change_health(self, ctx, member: discord.Member, value: int):
        user_id = str(member.id)
        self.ensure_user(user_id)

        maxhp = self.bot.user_data[user_id]["maxhealth"]
        value = max(0, min(value, maxhp))  # clamp

        self.bot.user_data[user_id]["health"] = value
        self.bot.save_data()

        await ctx.send(f"❤️ {member.mention} health set to **{value}/{maxhp}**")

    # --- changeMaxHealth ---
    @commands.command(name="changemaxhealth", aliases=["setmaxhealth", "maxhp", "setmaxhp", "maxhealth"])
    @commands.has_permissions(manage_guild=True)
    async def change_max_health(self, ctx, member: discord.Member, value: int):
        user_id = str(member.id)
        self.ensure_user(user_id)

        value = max(1, value)

        self.bot.user_data[user_id]["maxhealth"] = value
        # keep health valid
        self.bot.user_data[user_id]["health"] = min(
            self.bot.user_data[user_id]["health"], value
        )

        self.bot.save_data()
        await ctx.send(f"💖 {member.mention} max health set to **{value}**")

    # --- setAttribute ---
    @commands.command(name="setattribute", aliases=["setatt", "attr", "changeatt", "att"])
    @commands.has_permissions(manage_guild=True)
    async def set_attribute(self, ctx, member: discord.Member, attribute: str, value: int):
        attribute = attribute.upper()
        if attribute not in VALID_ATTRIBUTES:
            await ctx.send(f"❌ Invalid attribute. Valid: {', '.join(VALID_ATTRIBUTES)}")
            return

        user_id = str(member.id)
        self.ensure_user(user_id)

        self.bot.user_data[user_id]["attributes"][attribute] = value
        self.bot.save_data()

        await ctx.send(
            f"📊 {member.mention} **{attribute}** set to **{value}**"
        )

        # --- changeSanity ---
    @commands.command(name="changeSanity", aliases=["setsanity", "sanity", "setsan", "changesan", "san"])
    @commands.has_permissions(manage_guild=True)
    async def change_sanity(self, ctx, member: discord.Member, value: int):
        user_id = str(member.id)
        self.ensure_user(user_id)

        maxsanity = self.bot.user_data[user_id]["maxsanity"]
        value = max(0, min(value, maxsanity))  # clamp

        self.bot.user_data[user_id]["sanity"] = value
        self.bot.save_data()

        await ctx.send(f"❤👁️‍🗨️ {member.mention} sanity set to **{value}/{maxsanity}**")

    # --- changeMaxHealth ---
    @commands.command(name="changemaxsanity", aliases=["setmaxsanity", "maxsan", "setmaxsan", "maxsanity"])
    @commands.has_permissions(manage_guild=True)
    async def change_max_sanity(self, ctx, member: discord.Member, value: int):
        user_id = str(member.id)
        self.ensure_user(user_id)

        value = max(1, value)

        self.bot.user_data[user_id]["maxsanity"] = value
        self.bot.user_data[user_id]["sanity"] = min(
            self.bot.user_data[user_id]["sanity"], value
        )

        self.bot.save_data()
        await ctx.send(f"🧠 {member.mention} max sanity set to **{value}**")

    @commands.command(name="boost", aliases=["setboost", "giveboost"])
    @commands.has_permissions(manage_guild=True)
    async def set_boost(self, ctx, member: discord.Member, value: int):
        user_id = str(member.id)
        self.ensure_user(user_id)

        self.bot.user_data[user_id]["boost"] = value
        self.bot.save_data()

        sign = "+" if value >= 0 else ""
        await ctx.send(
            f"⚡ {member.mention} boost set to **{sign}{value}** "
            f"(applies to next roll only)"
        )

    @commands.command(name="addmodifier", aliases=["addmod", "modifier", "givemodifier", "givemod"])
    @commands.has_permissions(manage_guild=True)
    async def add_modifier(self, ctx, member: discord.Member, *, args: str):
        user_id = str(member.id)
        self.ensure_user(user_id)

        tokens = args.split()

        effects = {}
        name_parts = []

        i = 0
        while i < len(tokens):
            token = tokens[i].upper()

            # Attribute + value pair
            if token in VALID_ATTRIBUTES and i + 1 < len(tokens):
                try:
                    value = int(tokens[i + 1])
                    effects[token] = value
                    i += 2
                    continue
                except ValueError:
                    pass

            # Otherwise part of name
            name_parts.append(tokens[i])
            i += 1

        if not effects:
            await ctx.send("❌ You must specify at least one attribute and value.")
            return

        name = " ".join(name_parts).strip()
        if not name:
            await ctx.send("❌ Modifier name missing.")
            return

        modifier = {
            "name": name,
            "effects": effects
        }

        self.bot.user_data[user_id]["modifiers"].append(modifier)
        self.bot.save_data()

        effects_display = ", ".join(f"{k} {v:+d}" for k, v in effects.items())
        await ctx.send(
            f"🧩 Modifier **{name}** added to {member.mention}\n"
            f"📊 Effects: {effects_display}"
        )

    @commands.command(name="removemodifier", aliases=["delmodifier", "removemod", "delmod"])
    @commands.has_permissions(manage_guild=True)
    async def remove_modifier(self, ctx, member: discord.Member, *, name: str):
        user_id = str(member.id)
        self.ensure_user(user_id)

        modifiers = self.bot.user_data[user_id]["modifiers"]

        for mod in modifiers:
            if mod["name"].lower() == name.lower():
                modifiers.remove(mod)
                self.bot.save_data()
                await ctx.send(
                    f"🗑️ Modifier **{mod['name']}** removed from {member.mention}"
                )
                return

        await ctx.send("❌ Modifier not found.")

    @commands.command(name="changelevel", aliases=["setlevel", "level"])
    @commands.has_permissions(manage_guild=True)
    async def change_level(
            self,
            ctx,
            level: int,
            member: discord.Member = None
    ):
        # Target
        if member is None:
            member = ctx.author

        user_id = str(member.id)
        self.ensure_user(user_id)

        # Clamp level
        level = max(1, level)

        self.bot.user_data[user_id]["level"] = level
        self.bot.save_data()

        await ctx.send(
            f"📈 {member.mention} level set to **{level}**"
        )

    @commands.command(name="erasedata", aliases=["wipeuser", "resetuser", "deleteData", "wipedata"])
    @commands.has_permissions(manage_guild=True)
    async def erase_data(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_id = str(member.id)

        if user_id not in self.bot.user_data:
            await ctx.send(f"ℹ️ {member.mention} has no data to erase.")
            return

        del self.bot.user_data[user_id]
        self.bot.save_data()

        await ctx.send(f"🧨 All data for {member.mention} has been **completely erased**.")


async def setup(bot):
    await bot.add_cog(AttributesHandler(bot))