# -*- coding: UTF-8 -*-
from flask import Flask,render_template,flash,request,redirect,url_for,Markup
from werkzeug import secure_filename
import subprocess,os,shutil,zipfile
import sys,re
reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)
app.secret_key='ldx'
xmxqpath=os.path.join("/","data","nginx","nginx","html","xmxq_auto")
xmxqhtnlfile = os.path.join("/","data","nginx","nginx","html","xmxq_auto.html")

ALLOWED_EXTENSIONS = set(['zip'])

def movename(upload_path,newfile,oldfile):
    if os.path.isfile(oldfile):
        os.remove(oldfile)
    if os.path.isfile(newfile):
        os.rename(newfile,oldfile)
    if upload_path != newfile:
        print "Move"
        shutil.move(upload_path, newfile)

def runcmd(upload_path,newfile,project,flag):
    extpath= os.path.join(xmxqpath,project)
    oldfile = os.path.join(xmxqpath,project,"xmxqold.zip") 
    if flag == "1":
        movename(upload_path, newfile,oldfile)
    else:
        if not os.path.isfile(oldfile):
            return "null"
        movename(oldfile,oldfile, newfile)
    lists = extpath+"<br>"
    z = zipfile.ZipFile(newfile,'r')
    name="/tmp"
    for f in z.namelist():
        name = f.split("/")[0]

	try:
		name.decode("utf8")
		#print 'utf8'
		name = name
	except:
		pass
	try:
		name.decode("gbk")
		#print 'gbk'
		name = name.decode('gbk').encode('utf')
	except:
		pass

        if name[0] != "_":
                break
    z.close()
    delpath = os.path.join(extpath,"xmxq")
    namepath = os.path.join(extpath,str(name))
    if os.path.exists(delpath):
        shutil.rmtree(delpath)

    comm = "unzip -O cp936 -o "+newfile+" -d "+extpath 
    p = subprocess.Popen(comm,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline,b''):
        line = line.rstrip().decode('utf8')

    os.rename(namepath,delpath)
    return lists

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/upload",methods=["POST","GET"])
def upload():
    if request.method == "POST" and 'file' in request.files:
        dirs = request.form.get('dirs')
        if not dirs:
            flash("not chooes project")
            return redirect(url_for('update'))
        f = request.files['file']
        if file and allowed_file(f.filename):
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(basepath, 'static','uploads', str(dirs)+'xmqq.zip')
            f.save(upload_path)
            newfile = os.path.join(xmxqpath, str(dirs),"xmxq.zip")
            info = runcmd(upload_path,newfile,dirs,"1")
            flash(Markup(info))
            return redirect(url_for('index'))
        else:
            flash("Wrong file format(*.zip)")
    flash("not choose file")
    return redirect(url_for('update'))

def getProjectList():
    lists = []
    for li in os.listdir(xmxqpath):
        if os.path.isdir(os.path.join(xmxqpath,li)):
            lists.append(li)
    return lists

@app.route("/update",methods=["POST","GET"])
def update():
    lists = getProjectList()
    return render_template("update.html",projectlist = lists)

@app.route("/reduction",methods=["POST","GET"])
def reduction():
    if request.method == "POST":
        dirs = request.form.get('dirs')
        if not dirs:
            return redirect(url_for('reduction')) 
        newfile = os.path.join(xmxqpath, str(dirs),"xmxq.zip")
        info = runcmd(newfile,newfile,dirs,"2")
        flash(Markup(info))
        return redirect(url_for('index')) 
    lists = getProjectList()
    return render_template("reduction.html",projectlist = lists)


def readHtml():
    fn = open(xmxqhtnlfile,"r")
    readdata=fn.readlines()
    fn.close()
    return readdata

def createUrl(project,urlname,flag): 
    readdata = readHtml()
    fn = open(xmxqhtnlfile,"w")
    for data in readdata:
        if flag:
            if 'class="xmxq_auto"' in data:
                fn.write(data)
		fn.write('<h3><a href="http://172.16.124.3/xmxq_auto/'+project+'/xmxq/" target=_blank>'+urlname+'</a></h3>')
            else:
	        fn.write(data)
        else:
            poj = re.search('xmxq_auto\/(.*?)\/xmxq',data)
	    if poj and project == poj.group(1):
		tmp=re.sub(re.search('target=_blank>(.*?)<\/a>',data).group(1),urlname,data)
		fn.write(tmp)
	    else:
		fn.write(data)	
    fn.close()

def deleteUrl(project): 
    delpath = os.path.join(xmxqpath,str(project))
    if os.path.exists(delpath):
        shutil.rmtree(delpath)
    readdata = readHtml()
    fn = open(xmxqhtnlfile,"w")
    for data in readdata:
        poj = re.search('xmxq_auto\/(.*?)\/xmxq',data)
        if poj and project == poj.group(1):
            pass
	else:
   	    fn.write(data)	
    fn.close()

@app.route("/delete",methods=["POST","GET"])
def delete():
    if request.method == "POST":
        project = request.form.get('dirs')
        if not project:
            return redirect(url_for('delete'))
        deleteUrl(project)
        flash("delete "+str(project)+" success")
    lists = getProjectList()
    return render_template("delete.html",projectlist = lists)
    

@app.route("/create",methods=["POST","GET"])
def create():
    if request.method == "POST":
        urlname = request.form.get("urlname")
        project = request.form.get("projectname")
        if project:
            newproject = os.path.join(xmxqpath,project)
            if not os.path.isdir(newproject):
                os.mkdir(newproject)
                flash("create,success")
		createUrl(project,urlname,True)
            else:
                flash("project alive,Modify the success")
		createUrl(project,urlname,False)
            #return redirect(url_for('create'))
        else:
            flash("name err")
            #return redirect(url_for('create'))
    lists = getProjectList()
    return render_template("create.html",projectlist = lists)

@app.route("/choose",methods=["POST","GET"])
def choose():
    choose = request.form.get('choose')
    if choose == "create":
        return redirect(url_for('create'))
    elif choose == "update":
        return redirect(url_for('update'))
    elif choose == "delete":
	return redirect(url_for('delete'))
    else:
        return redirect(url_for("reduction"))

@app.route("/",methods=["GET","POST"])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=4906)
    pass
