from aiohttp import web
import os

async def runFile(request):
    filepath = request.match_info.get('filepath', "")
    filename = request.match_info.get('filename', "")
    arg1 = request.match_info.get('arg1', "")
    arg2 = request.match_info.get('arg2', "")
    if os.path.exists('./' + filepath + '/' +filename):
        text = "Received Request, Searching for " + filepath + '/' + filename.replace('.', '(dot)') + ", Found File, Running it."
        cwd = os.path.dirname(os.path.realpath(__file__))
        os.chdir(cwd + '/' + filepath)
        os.system('python ' + filename + ' {arg1} {arg2}'.format(arg1=arg1, arg2=arg2))
        os.chdir(cwd)
    else:
        text = "Received Request, Searching for " + filepath + '/' + filename.replace('.', '(dot)') + ", Did not find File."
    return web.Response(text=text)

app = web.Application()
app.router.add_get('/', runFile)
app.router.add_get('/{filename}', runFile)
app.router.add_get('/{filepath}/{filename}', runFile)
app.router.add_get('/{filepath}/{filename}/{arg1}', runFile)
app.router.add_get('/{filepath}/{filename}/{arg1}/{arg2}', runFile)
web.run_app(app, port=5858)