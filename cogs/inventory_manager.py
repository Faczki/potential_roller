import discord
from discord.ext import commands
import copy
from data_default import DEFAULT_USER
VALID_ARMOR_PIECES = {"head", "chest", "boots", "hands"}

class InventoryManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_inventory_weight(self, user_id):
        items = self.bot.user_data[user_id].get("items", {})
        return sum(
            item["amount"] * item["weight"]
            for item in items.values()
        )

    # --- Utility ---
    def ensure_user(self, user_id):
        if user_id not in self.bot.user_data:
            self.bot.user_data[user_id] = copy.deepcopy(DEFAULT_USER)

    # --- changeCash ---
    @commands.command(name="changecash", aliases=["setcash", "money", "setmoney", "cash"])
    @commands.has_permissions(manage_guild=True)
    async def change_cash(self, ctx, member: discord.Member, value: int):
        user_id = str(member.id)
        self.ensure_user(user_id)

        self.bot.user_data[user_id]["cash"] = max(0, value)
        self.bot.save_data()

        await ctx.send(f"💰 {member.mention} cash set to **{value}**")

    # --- changeWeapon ---
    @commands.command(name="changeweapon", aliases=["setweapon", "weapon"])
    @commands.has_permissions(manage_guild=True)
    async def change_weapon(self, ctx, member: discord.Member, *, weapon: str):
        user_id = str(member.id)
        self.ensure_user(user_id)

        self.bot.user_data[user_id]["weapon"] = weapon
        self.bot.save_data()

        await ctx.send(f"🗡️ {member.mention} weapon set to **{weapon}**")

    @commands.command(name="changesecondary", aliases=["setsecondary", "secondary"])
    @commands.has_permissions(manage_guild=True)
    async def change_secondary(self, ctx, member: discord.Member, *, seconda: str):
        user_id = str(member.id)
        self.ensure_user(user_id)

        self.bot.user_data[user_id]["secondary"] = seconda
        self.bot.save_data()

        await ctx.send(f"🗡️ {member.mention} secondary weapon set to **{seconda}**")

    @commands.command(name="setInvspace", aliases=["invspace", "changeInvspace", "inventoryspace"])
    @commands.has_permissions(manage_guild=True)
    async def setInvSpace(self, ctx, member: discord.Member, *, value: int):
        user_id = str(member.id)

        # Ensure user exists
        if user_id not in self.bot.user_data:
            self.bot.user_data[user_id] = copy.deepcopy(DEFAULT_USER)

        if value <= 0:
            await ctx.send("❌ Inventory space must be greater than 0.")
            return

        self.bot.user_data[user_id]["inventory_space"] = value
        self.bot.save_data()

        await ctx.send(
            f"🎒 {member.mention} inventory space set to **{value}**"
        )

    # --- addEquipment ---
    @commands.command(name="addequipment", aliases=["addequip"])
    @commands.has_permissions(manage_guild=True)
    async def add_equipment(self, ctx, member: discord.Member, *, name: str):
        user_id = str(member.id)
        self.ensure_user(user_id)

        equipments = self.bot.user_data[user_id]["equipments"]

        if name.lower() in (e.lower() for e in equipments):
            await ctx.send("❌ Equipment already added.")
            return

        equipments.append(name)
        self.bot.save_data()

        await ctx.send(f"📦 Equipment **{name}** added to {member.mention}")

    # --- removeEquipment ---
    @commands.command(name="removeequipment", aliases=["delequipment", "remequip", "removeequip", "delequip"])
    @commands.has_permissions(manage_guild=True)
    async def remove_equipment(self, ctx, member: discord.Member, *, name: str):
        user_id = str(member.id)
        self.ensure_user(user_id)

        equipments = self.bot.user_data[user_id]["equipments"]

        for item in equipments:
            if item.lower() == name.lower():
                equipments.remove(item)
                self.bot.save_data()
                await ctx.send(f"🗑️ Equipment **{item}** removed from {member.mention}")
                return

        await ctx.send("❌ Equipment not found.")

    @commands.command(name="additem", aliases=["giveitem", "item"])
    @commands.has_permissions(manage_guild=True)
    async def additem(
            self,
            ctx,
            member: discord.Member,
            amount: int,
            weight: int,
            *,
            text: str
    ):
        user_id = str(member.id)
        self.ensure_user(user_id)

        items = self.bot.user_data[user_id]["items"]

        # Split name / description using |
        if "|" in text:
            name, description = map(str.strip, text.split("|", 1))
        else:
            name = text.strip()
            description = None

        # Case-insensitive merge
        for item_name in items:
            if item_name.lower() == name.lower():
                items[item_name]["amount"] += amount
                self.bot.save_data()
                await ctx.send(
                    f"✅ Added **{amount}x {item_name}** to {member.mention}"
                )
                return

        # New item
        items[name] = {
            "amount": amount,
            "weight": weight,
            "description": description
        }

        self.bot.save_data()
        await ctx.send(
            f"✅ Added **{amount}x {name}** to {member.mention}"
        )

    @commands.command(name="removeitem", aliases=["delitem", "deleteitem", "remitem"])
    @commands.has_permissions(manage_guild=True)
    async def remove_item(
            self,
            ctx,
            member: discord.Member,
            amount: int,
            *,
            name: str
    ):
        user_id = str(member.id)
        self.ensure_user(user_id)

        items = self.bot.user_data[user_id]["items"]

        for item_name in list(items.keys()):
            if item_name.lower() == name.lower():
                if items[item_name]["amount"] < amount:
                    await ctx.send("❌ Not enough items to remove.")
                    return

                items[item_name]["amount"] -= amount

                if items[item_name]["amount"] <= 0:
                    del items[item_name]

                self.bot.save_data()
                await ctx.send(
                    f"🗑 Removed **{amount}x {item_name}** from {member.mention}"
                )
                return

        await ctx.send("❌ Item not found.")

    @commands.command(name="addarmor", aliases=["setarmor", "armor", "givearmor"])
    @commands.has_permissions(manage_guild=True)
    async def add_armor(
            self,
            ctx,
            member: discord.Member,
            armor_piece: str,
            *,
            name: str
    ):
        armor_piece = armor_piece.lower()

        if armor_piece not in VALID_ARMOR_PIECES:
            await ctx.send(
                f"❌ Invalid armor piece. Use: {', '.join(VALID_ARMOR_PIECES)}"
            )
            return

        user_id = str(member.id)

        # Ensure user exists
        if user_id not in self.bot.user_data:
            self.bot.user_data[user_id] = copy.deepcopy(DEFAULT_USER)

        self.bot.user_data[user_id]["armory"]["armor"][armor_piece] = name
        self.bot.save_data()

        await ctx.send(
            f"🛡️ {member.mention} equipped **{name}** on **{armor_piece.capitalize()}**"
        )

    @commands.command(name="removearmor", aliases=["delarmor", "cleararmor", "dearmor"])
    @commands.has_permissions(manage_guild=True)
    async def remove_armor(
            self,
            ctx,
            member: discord.Member,
            armor_piece: str
    ):
        armor_piece = armor_piece.lower()

        if armor_piece not in VALID_ARMOR_PIECES:
            await ctx.send(
                f"❌ Invalid armor piece. Use: {', '.join(VALID_ARMOR_PIECES)}"
            )
            return

        user_id = str(member.id)

        if user_id not in self.bot.user_data:
            await ctx.send("❌ User has no data.")
            return

        if self.bot.user_data[user_id]["armory"]["armor"][armor_piece] == "Nenhum":
            await ctx.send("ℹ️ No armor equipped in that slot.")
            return

        removed = self.bot.user_data[user_id]["armory"]["armor"][armor_piece]
        self.bot.user_data[user_id]["armory"]["armor"][armor_piece] = "Nenhum"
        self.bot.save_data()

        await ctx.send(
            f"🗑️ Removed **{removed}** from {member.mention}'s **{armor_piece.capitalize()}** slot"
        )

async def setup(bot):
    await bot.add_cog(InventoryManager(bot))