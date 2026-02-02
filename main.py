from discord.ext import commands
import discord

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # HELP COMMAND
    # =========================
    @commands.command(name="help", aliases=["h", "ajuda", "socorro", "support"])
    async def help(self, ctx):
        embed = discord.Embed(
            title="📖 Ajuda",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🎲 Rolls",
            value=(
                "`.roll [atributo] [perícia]` – Rolagem padrão\n"
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

            embed.add_field(
                name="✨ Atributos",
                value=(
                    "`.addmodifier`, `.removemodifier`\n"
                    "`.changehealth`, `.changemaxhealth`\n"
                    "`.changesanity`, `.changemaxsanity`\n"
                    "`.setattribute`, `.boost`\n"
                    "`.changelevel`, `.erasedata`"
                ),
                inline=False
            )

            embed.add_field(
                name="🎒 Inventário",
                value=(
                    "`.addequipment`, `.removeequipment`\n"
                    "`.additem`, `.removeitem`\n"
                    "`.changecash`, `.changeweapon`\n"
                    "`.changesecondary`, `.setinvspace`\n"
                    "`.addarmor`, `.removearmor`"
                ),
                inline=False
            )

        embed.set_footer(text="Potential Roller 🫃 – Todos os Direitos Reservados (Provavelmente)")
        await ctx.send(embed=embed)

    # =========================
    # EMBED COMMAND
    # =========================
    @commands.command(name="embed", aliases=["createembed", "newembed"])
    @commands.has_permissions(manage_guild=True)
    async def embed(self, ctx, color: str, title: str, *, content: str):
        try:
            color = discord.Color(int(color.replace("#", ""), 16))
        except ValueError:
            await ctx.send("❌ Invalid color. Use hex like `#ff0000`.")
            return

        lines = content.splitlines()
        description = []
        fields = []

        for line in lines:
            if line.lower().startswith("field:"):
                try:
                    name, value = line[6:].split("|", 1)
                    fields.append((name.strip(), value.strip()))
                except ValueError:
                    continue
            else:
                description.append(line)

        embed = discord.Embed(
            title=title,
            description="\n".join(description),
            color=color
        )

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(System(bot))