#MIT License

#Copyright (c) 2024 H_ONEYSINGH-X-Userbot

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import asyncio
import socket
import sys
from datetime import datetime
from os import environ, execle, path, remove

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from pyrogram import Client, filters
from pyrogram.types import Message

from config import BRANCH
from config import CMD_HANDLER as cmd
from config import GIT_TOKEN, HEROKU_API_KEY, HEROKU_APP_NAME, REPO_URL
from X.helpers.adminHelpers import DEVS
from config import SUDO_USERS
from X.helpers.basic import edit_or_reply
from X.helpers.misc import HAPP, XCB
from X.helpers.tools import get_arg
from X.utils.misc import restart
from X.utils.pastebin import PasteBin
from X.utils.tools import bash

from .help import add_command_help

if GIT_TOKEN:
    GIT_USERNAME = REPO_URL.split("com/")[1].split("/")[0]
    TEMP_REPO = REPO_URL.split("https://")[1]
    UPSTREAM_REPO = f"https://{GIT_USERNAME}:{GIT_TOKEN}@{TEMP_REPO}"
    UPSTREAM_REPO_URL = UPSTREAM_REPO
else:
    UPSTREAM_REPO_URL = REPO_URL

requirements_path = path.join(
    path.dirname(path.dirname(path.dirname(__file__))), "requirements.txt"
)


async def is_heroku():
    return "heroku" in socket.getfqdn()


async def gen_chlog(repo, diff):
    ch_log = ""
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"• [{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n"
        )
    return ch_log


async def updateme_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


@Client.on_message(
    filters.command("diupdate", ["."]) & filters.user(DEVS) & ~filters.me
)
@Client.on_message(filters.command("update", cmd) & filters.me)
@Client.on_message(
    filters.command(["update"], ".") & (filters.me | filters.user(SUDO_USERS))
)
async def upstream(client: Client, message: Message):
    status = await edit_or_reply(message, "`Checking for Updates, Wait a Moment Master...`")
    conf = get_arg(message)
    off_repo = UPSTREAM_REPO_URL
    try:
        txt = (
            "**Update Cannot Continue Due to "
            + "Some ERROR Occurred**\n\n**LOGTRACE:**\n"
        )
        repo = Repo()
    except NoSuchPathError as error:
        await status.edit(f"{txt}\n**Directory** `{error}` **Can not be found.**")
        repo.__del__()
        return
    except GitCommandError as error:
        await status.edit(f"{txt}\n**Early failure!** `{error}`")
        repo.__del__()
        return
    except InvalidGitRepositoryError:
        if conf != "deploy":
            pass
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        repo.create_head(
            BRANCH,
            origin.refs[BRANCH],
        )
        repo.heads[BRANCH].set_tracking_branch(origin.refs[BRANCH])
        repo.heads[BRANCH].checkout(True)
    ac_br = repo.active_branch.name
    if ac_br != BRANCH:
        await status.edit(
            f"**[UPDATER]:** `Looks like you are using your own custom branch ({ac_br}). in that case, Updater is unable to identify which branch is to be merged. please checkout to main branch`"
        )
        repo.__del__()
        return
    try:
        repo.create_remote("upstream", off_repo)
    except BaseException:
        pass
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)
    changelog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    if "deploy" not in conf:
        if changelog:
            changelog_str = f"**Update Available For Branch [{ac_br}]:\n\nCHANGELOG:**\n\n`{changelog}`"
            if len(changelog_str) > 4096:
                await status.edit("**The changelog is too big, sent as a file.**")
                file = open("output.txt", "w+")
                file.write(changelog_str)
                file.close()
                await client.send_document(
                    message.chat.id,
                    "output.txt",
                    caption=f"**Type** `{cmd}update deploy` **To Update Userbot.**",
                    reply_to_message_id=status.id,
                )
                remove("output.txt")
            else:
                return await status.edit(
                    f"{changelog_str}\n**Type** `{cmd}update deploy` **To Update Userbot.**",
                    disable_web_page_preview=True,
                )
        else:
            await status.edit(
                f"\n`Your BOT is`  **up-to-date**  `with branch master`  **[{ac_br}]**\n",
                disable_web_page_preview=True,
            )
            repo.__del__()
            return
    if HEROKU_API_KEY is not None:
        import heroku3

        heroku = heroku3.from_key(HEROKU_API_KEY)
        heroku_app = None
        heroku_applications = heroku.apps()
        if not HEROKU_APP_NAME:
            await status.edit(
                "`Please set up the HEROKU_APP_NAME variable to be able to update userbot.`"
            )
            repo.__del__()
            return
        for app in heroku_applications:
            if app.name == HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await status.edit(
                f"{txt}\n`Invalid Heroku credentials for updating userbot dyno.`"
            )
            repo.__del__()
            return
        await status.edit(
            "`[HEROKU]: Update Deploy H_ONEYSINGH X Userbot In process...`"
        )
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + HEROKU_API_KEY + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec="HEAD:refs/heads/main", force=True)
        except GitCommandError:
            pass
        await status.edit(
            "`H_ONEYSINGH X Userbot Updated Successfully! Userbot can be used again.`"
        )
    else:
        try:
            ups_rem.pull(ac_br)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await updateme_requirements()
        await status.edit(
            "`H_ONEYSINGH X Userbot Updated Successfully! Userbot can be used again.`",
        )
        args = [sys.executable, "-m", "X"]
        execle(sys.executable, *args, environ)
        return


@Client.on_message(filters.command("cupdate", ["."]) & filters.user(DEVS) & ~filters.me)
@Client.on_message(filters.command("updatedeploy", cmd) & filters.me)
@Client.on_message(
    filters.command(["updatedeploy"], ".") & (filters.me | filters.user(SUDO_USERS))
)
async def updaterman(client: Client, message: Message):
    if await is_heroku():
        if HAPP is None:
            return await edit_or_reply(
                message,
                "Make sure HEROKU_API_KEY and HEROKU_APP_NAME you are properly configured in heroku config vars",
            )
    response = await edit_or_reply(message, "Checking for available updates...")
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit("Git Command Error")
    except InvalidGitRepositoryError:
        return await response.edit("Invalid Git Repsitory")
    to_exc = f"git fetch origin {BRANCH} &> /dev/null"
    await bash(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]  # main git repository
    for checks in repo.iter_commits(f"HEAD..origin/{BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("Bot is up-to-date!")
    updates = ""
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[(format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4],
    )
    for info in repo.iter_commits(f"HEAD..origin/{BRANCH}"):
        updates += f"<b>➣ #{info.count()}: [{info.summary}]({REPO_}/commit/{info}) by -> {info.author}</b>\n\t\t\t\t<b>➥ Commited on:</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
    _update_response_ = "<b>A new update is available for the Bot!</b>\n\n➣ Pushing Updates Now</code>\n\n**<u>Updates:</u>**\n\n"
    _final_updates_ = _update_response_ + updates
    if len(_final_updates_) > 4096:
        url = await PasteBin(updates)
        nrs = await response.edit(
            f"<b>A new update is available for the Bot!</b>\n\n➣ Pushing Updates Now</code>\n\n**<u>Updates:</u>**\n\n[Click Here to checkout Updates]({url})"
        )
    else:
        nrs = await response.edit(_final_updates_, disable_web_page_preview=True)
    await bash("git stash &> /dev/null && git pull")
    if await is_heroku():
        try:
            await response.edit(
                f"{nrs.text}\n\nBot was updated successfully on Heroku! Now, wait for 2 - 3 mins until the bot restarts!"
            )
            await bash(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            return await response.edit(f"{nrs.text}\n\nERROR: <code>{err}</code>")
    else:
        await bash("pip3 install -r requirements.txt")
        restart()
        exit()


add_command_help(
    "•─╼⃝𖠁 ᴜᴘᴅᴀᴛᴇ",
    [
        ["update", "Tᴏ ꜱᴇᴇ ᴀ ʟɪꜱᴛ ᴏғ ᴛʜᴇ ʟᴀᴛᴇꜱᴛ ᴜᴘᴅᴀᴛᴇꜱ ғʀᴏᴍ Jᴀᴘᴀɴᴇꜱᴇ-X-Uꜱᴇʀʙᴏᴛ."],
        ["update deploy", "Tᴏ ᴜᴘᴅᴀᴛᴇ ᴜꜱᴇʀʙᴏᴛ."],
    ],
  )
