from discord.ext import commands
import discord

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h", "ajuda", "socorro", "support"])
    async def help(self, ctx):
        embed = discord.Embed(
            title="📖 Ajuda",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🎲 Rolls",
            value=(
                "`.roll [atributo] [perícia]` – Rolagem padrão com atributos\n"
                "`.d20`, `.2d10`, `.d6` – Rolagens de dado"
            ),
            inline=False
        )

        embed.add_field(
            name="📊 Stats",
            value=(
                "`.stats` – Mostra seu perfil\n"
                "`.inventory` – Mostra seu inventário\n"
                "`.help` – Mostra essa mensagem"
            ),
            inline=False
        )

        if ctx.author.guild_permissions.manage_guild:
            embed.add_field(
                name="🧪 Buffs e Debuffs",
                value=(
                    "`.addbuff`, `.removebuff`\n"
                    "`.adddebuff`, `.removedebuff`\n"
                    "`.clearbuffs`, `.cleardebuffs`"
                ),
                inline=False
            )

            if ctx.author.guild_permissions.manage_guild:
                embed.add_field(
                    name="✨ Atributos",
                    value=(
                        "`.addmodifier`, `.removemodifier`\n"
                        "`.changehealth`, `.changemaxhealth`\n"
                        "`.changesanity`, `.changemaxsanity`\n"
                        "`.setattribute`, `.boost`\n"
                        "`.changeLevel`, `.eraseData`"
                    ),
                    inline=False
                )

            if ctx.author.guild_permissions.manage_guild:
                embed.add_field(
                    name="🎒 Inventário",
                    value=(
                        "`.addequipment`, `.removeequipment`\n"
                        "`.additem`, `.removeitem`\n"
                        "`.changecash`, `.changeweapon`\n"
                        "`.changeSecondary`, `.setInvSpace`\n"
                        "`.addArmor`, `.removearmor`"
                    ),
                    inline=False
                )

        embed.set_footer(text="Potential Roller 🫃 – Todos os Direitos Reservados (Provavelmente)")

        @commands.command(name="embedtest")
        async def embedtest(self, ctx):
            embed = discord.Embed(
                title="Teste",
                description="Se você está vendo isso, embeds funcionam.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(System(bot))