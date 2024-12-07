import discord
from discord.ext import commands
from core.commands.cleant.interface import CleantCommandInterface

class CleantCommand(CleantCommandInterface):
    async def clean_channel(self, ctx: commands.Context):
        """
        Limpa todas as mensagens do canal atual.
        """
        try:
            await ctx.channel.purge()
            confirmation_message = await ctx.send("🧹 Chat limpo com sucesso!")
            await confirmation_message.delete(delay=5)
        except discord.Forbidden:
            await self.handle_permission_error(ctx)
        except Exception as e:
            await self.handle_generic_error(ctx, e)

    async def handle_permission_error(self, ctx: commands.Context):
        """
        Envia uma mensagem caso o bot não tenha permissão para apagar mensagens.
        """
        await ctx.send("❌ Não tenho permissão para apagar mensagens neste canal.")

    async def handle_generic_error(self, ctx: commands.Context, error: Exception):
        """
        Envia uma mensagem para tratar erros genéricos.
        """
        await ctx.send(f"❌ Ocorreu um erro ao tentar limpar o chat: {error}")

@commands.command(name="cleant", help="Limpa o chat atual. Apenas administradores podem usar este comando.")
@commands.has_permissions(administrator=True)
async def cleant(ctx):
    """
    Comando para limpar mensagens do chat atual.
    Apenas administradores podem executar este comando.
    """
    command = CleantCommand()
    await command.clean_channel(ctx)
