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
import json
from rpcclient import client_rpc

def list_images():
    '''List the images for a project.
    '''
    if request.env.request_method == "POST":
     project = request.vars["project"]
     if project == "bmi_infra":        ## for the time being hard coded project. We will add DB support in multi-tanency TODO
	list_return = client_rpc(['list_all_images'])
        status_code = list_return['status_code']
        if status_code == 200: 
            image_list = list_return['retval']
            response.body = json.dumps(image_list)
	    return response.body
        else:
            response.status = list_return['status_code'] 
            response.body = json.dumps(list_return['msg'])
            return response.body
    else:
        response.status = 444
	return 'Please use a POST'
 
def provision_node():
    '''
    Node is the physical node name that we get from HaaS
    '''
    if request.env.request_method == "PUT":
     node_name = request.vars["node"]
     img_name = request.vars["img"]
     project = request.vars["project"]
     snap_name = request.vars["snap_name"]
     if project == 'bmi_infra':
    	ret = client_rpc(['provision', node_name, img_name, snap_name])
	if ret['status_code'] == 200:
		response.body = ret['retval']
		response.status = 200
		return response.status
	else:
		response.status = ret['status_code']
		response.body = ret['msg']
		return response.body
    else:
	response.status = 444
        return 'Please use a PUT'

def remove_node():
    '''
    Node is the physical node that you want to dissociate
    '''
    if request.env.request_method == "DELETE":
     node_name = request.vars["node"]
     project = request.vars["project"]
     if project == 'bmi_infra':
       ret = client_rpc(['detach_node',node_name])
       if ret['status_code'] == 200:
                response.body = ret['retval']
                response.status = 200
		return response.status
       else:
                response.status = ret['status_code']
                response.body = ret['msg']
		return response.status
    else:
		response.status = 444		
    		return 'Please use a DELETE'

def snap_image():
    '''
    Node is the physical node that you want to dissociate
    '''
    if request.env.request_method == "PUT":
     img_name = request.vars["img"]
     snap_name = request.vars["snap_name"]
     project = request.vars["project"]
     if project == 'bmi_infra':
       ret = client_rpc(['create_snapshot', img_name, snap_name])
       if ret['status_code'] == 200:
                response.body = ret['retval']
                response.status = 200
		return response.status
       else:
                response.status = ret['status_code']
                response.body = ret['msg']
		return response.status
    else:
		response.status = 444		
    		return 'Please use a PUT'


def list_snapshots():
    '''
    List all snapshots for the given image
    '''
    if request.env.request_method == "POST":
     img_name = request.vars["img"]
     project = request.vars["project"]
     if project == 'bmi_infra':
       ret = client_rpc(["list_snaps", img_name])
       if ret['status_code'] == 200:
                response.body = ret['retval']
                response.status = 200
		return json.dumps(response.body)
       else:
                response.status = ret['status_code']
                response.body = ret['msg']
		return response.body
    else:
		response.status = 444		
    		return "Please use a POST"

def remove_snapshot():
    '''
    Removes the given snapshot for the given image
    '''
    if request.env.request_method == "DELETE":
     img_name = request.vars["img"]
     project = request.vars["project"]
     snap_name = request.vars["snap_name"]
     if project == 'bmi_infra':
       ret = client_rpc(["remove_snaps", img_name, snap_name])
       if ret['status_code'] == 200:
                response.body = ret['retval']
                response.status = 200
		return response.status
       else:
                response.status = ret['status_code']
                response.body = ret['msg']
		return response.status
    else:
		response.status = 444		
    		return 'Please use a DELETE'

   
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
