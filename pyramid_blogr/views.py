from pyramid.response import Response
from pyramid.renderers import render
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from sqlalchemy.exc import DBAPIError
from sqlalchemy import desc
from models import DBSession, User, Article, Base
from datetime import *

def get_user(user_name):
    if user_name!=None:
        return DBSession.query(User).filter(User.name==user_name).first()
    else:return None

@view_config(route_name='home', renderer='/')
def home(request):
    return HTTPFound(location='/login')

@view_config(route_name='about',renderer='templates/contact.jinja2')
def about(request):
    return {}
    
@view_config(route_name='view_blog',renderer='templates/index.jinja2')
def view_blog(request):   
    return {'posts' : DBSession.query(Article).order_by(Article.id_A.desc()).all(),
            'onuser' : get_user(request.authenticated_userid)}

@view_config(route_name='view_my',renderer='templates/my.jinja2')
def view_my(request):
    return {'onuser' : get_user(request.authenticated_userid)}


@view_config(route_name='blog_article',renderer='templates/post.jinja2')
def blog_article(request):
    idP = request.matchdict.get('id')
    post = DBSession.query(Article).filter(Article.id_A==idP).first()
    return {'post' : post,
            'onuser': get_user(request.authenticated_userid)}


@view_config(route_name='blog_create', renderer='templates/newPost.jinja2')
def blog_create(request):
    if 'POST'==request.method:
        Ptitle = request.params['title']
        Pcontent = request.params['content']
        articlee = Article(title=Ptitle, content=Pcontent, u_id=get_user(request.authenticated_userid).id_U, u_n=get_user(request.authenticated_userid).name, Cdate=datetime.now())
        DBSession.add(articlee)
        DBSession.commit
        return HTTPFound(location = '/index')
    else: return{'onuser' : get_user(request.authenticated_userid)}

@view_config(route_name='login', renderer='templates/autorisation.jinja2')
def login(request):
    headers=forget(request)
    HTTPFound(location='/login')
    if 'POST'==request.method:
        login = request.params['login']
        password_ = request.params['password']
        user = DBSession.query(User).filter(User.name==login).first()
        if user!=None and user.password == password_:
            headers = remember(request, login)
            return HTTPFound(location='/index', headers=headers)
        else:
            return {'message':"Incorrect"}
    return{'onuser' : get_user(request.authenticated_userid)}

@view_config(route_name='logout')
def logout(request):
    headers=forget(request)
    return HTTPFound(location = '/', headers=headers)
        
@view_config(route_name='register', renderer='templates/registration.jinja2')
def register(request):
    if (get_user(request.authenticated_userid)!=None):
        headers=forget(request)
    if request.method =='POST':
        Uname = request.params['username']
        Upassword = request.params['password']
        Uabout = request.params['aboutme']
        user = DBSession.query(User).filter(User.name==Uname).first()
        if user==None:
            if Uname!=None and Uname!="" and Upassword!=None and Upassword!="":
                DBSession.add(User(name=Uname, password=Upassword, aboutme=Uabout))
                DBSession.commit
                headers = remember(request, User.name)
                return HTTPFound(location='/', headers=headers)
            else: return {'message':"notenough"}
        else: return {'message':"login"}
    return{'onuser' : get_user(request.authenticated_userid)}
