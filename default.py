# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
import os
import subprocess
import sys

from wrapper_create_env import  *

def clean_bigdata_env():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    #response.flash = T("Hello World")
    #create_output=subprocess.call(['python','/home/Users/ravisantoshgudimetla/Downloads/wrapper_create_env.py','/home/ravig/gitrepo/ims/metalHadoopOnDemand_ravi/haas_master/cleanBigDataEnvNew.sh bmi_infra'])
    file_path = "/home/ravig/gitrepo/ims/metalHadoopOnDemand_ravi/haas_master/cleanBigDataEnvNew.sh"
    ssh_path = ["ssh", "-A", "-t", '-t', "ravig@129.10.3.48", "-C"] 
    command_args = ["bmi_infra"] 
    # Project hardcoding is necessary to avoid ssh shell-escape 
    #command execution. We need to write some funtions to sanitize user provided inputs.
    try:
        return_list = call_shellscript(file_path,command_args, ssh_path)
        return_list_parsed = parse_stdout_output(return_list, ("cleanBigDataEnvNew"))
    except UnboundLocalError as exception:
        return "Call returned malformed output"
    return return_list_parsed
    #return dict(message=T(str(request.vars["jj"])))

def create_bigdata_env():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    #response.flash = T("Hello World")
    #create_output=subprocess.call(['python','/home/Users/ravisantoshgudimetla/Downloads/wrapper_create_env.py','/home/ravig/gitrepo/ims/metalHadoopOnDemand_ravi/haas_master/cleanBigDataEnvNew.sh bmi_infra'])
    file_path = "/home/ravig/gitrepo/ims/metalHadoopOnDemand_ravi/haas_master/createBigDataEnvNew.sh"
    ssh_path = ["ssh", "-A", "-t", '-t', "ravig@129.10.3.48", "-C"] 
    node_count = request.vars["nc"]
    try:
        node_count = int(node_count)
    except ValueError as e:
        return dict(message=T(str("Invalid Count. Please check count")))
    command_args = ["bmi_infra", str(node_count)]
    try:
        return_list = call_shellscript(file_path,command_args, ssh_path)
        return_list_parsed = parse_stdout_output(return_list, ("createBigDataEnvNew"))
    except UnboundLocalError as exception:
        return "Call returned malformed output"
    return return_list_parsed
    #return dict(message=T(str(request.vars["jj"])))

    
    
    
    
    
    
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
