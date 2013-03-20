#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


try:
  import json
except ImportError:
  import simplejson as json
import posixpath

from hadoop.fs.hadoopfs import Hdfs
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from oozie.models import Workflow


# To move somewhere else when official commit
class Document(models.Model):
  owner = models.ForeignKey(User, db_index=True, verbose_name=_t('Owner'), help_text=_t('Person who can modify the job.'))
  is_history = models.BooleanField(default=False, db_index=True, verbose_name=_t('Is managed'),
                                  help_text=_t('If the job should show up in the history'))


class PigScript(Document):
  _ATTRIBUTES = ['script', 'name', 'properties']
  
  data = models.TextField(default=json.dumps({'script': '', 'name': ''}))
    
  def update_from_dict(self, attrs):
    data_dict = self.dict
    
    if attrs.get('script'):
      data_dict['script'] = attrs['script']

    if attrs.get('name'):
      data_dict['name'] = attrs['name']

    self.data = json.dumps(data_dict)
    
  @property
  def dict(self):
    return json.loads(self.data)
  
  
class Submission(models.Model):
  script = models.ForeignKey(PigScript)
  workflow = models.ForeignKey(Workflow)
  

class Udf:
  pass


def get_workflow_output(oozie_workflow, fs):
  output = None

  if 'workflowRoot' in oozie_workflow.conf_dict:
    output = oozie_workflow.conf_dict.get('workflowRoot')
    if output and not fs.exists(output):
      output = None

  return output


def hdfs_link(url):
  if url:
    path = Hdfs.urlsplit(url)[2]
    if path:
      if path.startswith(posixpath.sep):
        return "/filebrowser/view" + path
      else:
        return "/filebrowser/home_relative_view/" + path
    else:
      return url
  else:
    return url
