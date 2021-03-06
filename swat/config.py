#!/usr/bin/env python
# encoding: utf-8
#
# Copyright SAS Institute
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

'''
Initialization of SWAT options

'''

from __future__ import print_function, division, absolute_import, unicode_literals

import functools
from .clib import InitializeTK
from .utils.config import (register_option, check_boolean, check_int, get_option,
                           set_option, reset_option, describe_option, check_url,
                           SWATOptionError, check_string, options, get_suboptions,
                           get_default, check_float, option_context)
from .utils.compat import a2n

#
# TK options
#


def set_tkpath(val):
    ''' Check and set the TK path '''
    if val is None:
        return
    path = check_string(val)
    InitializeTK(a2n(path, 'utf-8'))
    return path


def _initialize_tkpath():
    ''' Check for TKPATH locations '''
    import os
    if 'TKPATH' in os.environ:
        return os.environ['TKPATH']

    import sys
    platform = 'linux'
    if sys.platform.lower().startswith('win'):
        platform = 'win'
    elif sys.platform.lower().startswith('darwin'):
        platform = 'mac'

    # See if the lib/<platform>/ directory has files in it.
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib', platform))
    if os.path.isdir(path) and len(os.listdir(path)) > 20:
        return path


register_option('tkpath', 'string', set_tkpath, _initialize_tkpath(),
                'Displays the path for SAS TK components.  This is determined\n' +
                'when SWAT is imported.  By default, it points to the platform\n' +
                'directory under the swat.lib module.  It can be overridden by\n' +
                'setting a TKPATH environment variable.')

#
# General options
#

register_option('encoding_errors', 'string', check_string, 'strict',
                'Specifies the error handler for encoding and decoding errors in\n' +
                'handling strings.  Possible values are given in the Python\n' +
                'documentation.  Typical values are strict, ignore, replace, or\n' +
                'xmlcharrefreplace.')

register_option('interactive_mode', 'boolean', check_boolean, True,
                'Indicates whether all interactive mode features should be enabled.\n' +
                'Interactive features include things like generating formatted help\n' +
                'strings for objects automatically generated from information from\n' +
                'the server.  This may give a performance improvement in batch jobs\n' +
                'that don\'t need interactive features.')

#
# CAS connection options
#

register_option('cas.print_messages', 'boolean', check_boolean, True,
                'Indicates whether or not CAS response messages should be printed.')

register_option('cas.trace_actions', 'boolean', check_boolean, False,
                'Indicates whether or not CAS action names and parameters should\n' +
                'be printed.  This can be helpful in debugging incorrect action\n' +
                'parameters.')

register_option('cas.trace_ui_actions', 'boolean', check_boolean, False,
                'Indicates whether or not CAS action names and parameters from\n' +
                'actions invoked by the interface itself. should be printed.\n' +
                'This option is only honored if cas.trace_actions is also enabled.')

register_option('cas.hostname', 'string', check_string,
                'localhost',
                'Specifies the hostname for the CAS server.',
                environ='CASHOST')

register_option('cas.port', 'int', check_int, 0,
                'Sets the port number for the CAS server.',
                environ='CASPORT')

register_option('cas.protocol', 'string',
                functools.partial(check_string,
                                  valid_values=['auto', 'cas', 'http', 'https']),
                'auto',
                'Communication protocol for talking to CAS server.\n' +
                'The value of "auto" will try to auto-detect the type.\n' +
                'Using "http" or "https" will use the REST interface.',
                environ='CASPROTOCOL')


def check_severity(sev):
    ''' Make sure the severity is None or an int '''
    if sev is None:
        return None
    return check_int(sev, maximum=2, minimum=0)


register_option('cas.exception_on_severity', 'int or None', check_severity, None,
                'Indicates the CAS action severity level at which an exception\n' +
                'should be raised.  None means that no exception should be raised.\n' +
                '1 would raise exceptions on warnings.  2 would raise exceptions\n' +
                'on errors.')

#
# Tabular data options
#

register_option('cas.dataset.format', 'string',
                functools.partial(check_string,
                                  valid_values=['dataframe:sas', 'dataframe',
                                                'dict', 'dict:list',
                                                'dict:series', 'dict:split',
                                                'dict:records', 'tuple']),
                'dataframe:sas',
                'Data structure for tabular data returned from CAS.  The following\n' +
                'formats are supported.\n'
                'dataframe:sas : Pandas Dataframe extended with SAS metadata such as\n' +
                '    SAS data formats, titles, labels, etc.\n' +
                'dataframe : Standard Pandas Dataframe\n' +
                'dict : Dictionary like {column => {index => value}}\n' +
                'dict:list : Dictionary like {column => [values]}\n' +
                'dict:series : Dictionary like {column => pandas.Series(values)\n' +
                'dict:split : Dictionary like {index => [index],\n' +
                '                              columns => [columns],\n' +
                '                              data => [values]}\n' +
                'dict:records : List like [{column => value}, ... ,\n' +
                '                          {column => value}]\n' +
                'tuple : A tuple where each element is a tuple of the data values only.')

register_option('cas.dataset.auto_castable', 'boolean', check_boolean, True,
                'Should a column of CASTable objects be automatically\n' +
                'created if a CASLib and CAS table name are columns in the data?\n' +
                'NOTE: This applies to all except the \'tuples\' format.')


def check_string_list(val):
    ''' Verify that value is a string or list of strings '''
    if isinstance(val, (list, set, tuple)):
        for item in val:
            check_string(item)
        return val
    return check_string(val)


register_option('cas.dataset.index_name', 'string or list of strings',
                check_string_list, '_Index_',
                'The name or names of the columns to be automatically converted\n' +
                'to the index.')

register_option('cas.dataset.drop_index_name', 'boolean', check_boolean, True,
                'If True, the name of the index is set to None.')

register_option('cas.dataset.index_adjustment', 'int', check_int, -1,
                'Adjustment to the index specified by cas.dataset.index.\n' +
                'This can be used to adjust SAS 1-based index data sets to\n' +
                '0-based Pandas DataFrames.')

register_option('cas.dataset.max_rows_fetched', 'int', check_int, 10000,
                'The maximum number of rows to fetch with methods that use\n' +
                'the table.fetch action in the background (i.e. the head, tail,\n' +
                'values, etc. of CASTable).')

register_option('cas.dataset.bygroup_columns', 'string',
                functools.partial(check_string,
                                  valid_values=['none', 'raw', 'formatted', 'both']),
                'formatted',
                'CAS returns by grouping information as metadata on a table.\n' +
                'This metadata can be used to construct columns in the output table.\n' +
                'The possible values of this option are:\n' +
                '    none : Do not convert metadata to columns\n' +
                '    raw  : Use the raw (i.e., unformatted) values\n' +
                '    formatted : Use the formatted value.  This is the actual value\n' +
                '                used to do the grouping\n' +
                '    both : Add columns for both raw and formatted')

register_option('cas.dataset.bygroup_formatted_suffix', 'string', check_string, '_f',
                'Suffix to use on the formatted column name when both raw and\n' +
                'formatted by group colunms are added.')

register_option('cas.dataset.bygroup_collision_suffix', 'string', check_string, '_by',
                'Suffix to use on the By group column name when a By group column\n' +
                'is also included as a data column.')

register_option('cas.dataset.bygroup_as_index', 'boolean', check_boolean, True,
                'If True, any by group columns are set as the DataFrame index.')

#
# IPython notebook options
#
#
# register_option('display.max_rows', 'int', check_int,
#                 pd.get_option('display.max_rows'),
#                 'Sets the maximum number of rows to be output for\n' +
#                 'any of the rendered output types.')
#
#
# def check_show_dimensions(value):
#     ''' Check for True, False, or 'truncate' '''
#     if isinstance(value, text_types) or isinstance(value, binary_types):
#         if value.lower() == 'truncate':
#             return value.lower()
#         raise SWATOptionError('Invalid string value given')
#     return check_boolean(value)
#
#
# register_option('display.show_dimensions', 'boolean or \'truncate\'',
#                 check_show_dimensions, pd.get_option('display.show_dimensions'),
#                 'Whether to print the dimensions at the bottom of a\n' +
#                 'SASDataFrame rendering.  If \'truncate\' is specified,\n' +
#                 'it will only print the dimensions if not all rows are displayed.')
#
# register_option('display.notebook.repr_html', 'boolean', check_boolean,
#                 pd.get_option('display.notebook_repr_html'),
#                 'When True, IPython notebook will use HTML representation for\n' +
#                 'for swat objects.  If display.notebook.repr_javascript is set,\n' +
#                 'that will take precedence over this rendering.')
#
# register_option('display.notebook.repr_javascript', 'boolean', check_boolean, False,
#                 'When True, IPython notebook will use javascript representation for\n' +
#                 'for swat objects.')
#
# register_option('display.notebook.css.datatables', 'URL', check_url,
#                 '//cdn.datatables.net/1.10.3/css/jquery.dataTables.min.css',
#                 'URL for the jQuery Datatables plugin CSS file')
#
# register_option('display.notebook.css.swat', 'URL', check_url,
#                 '//www.sas.com/cas/python/css/swat.css',
#                 'URL for the SWAT CSS file')
#
# register_option('display.notebook.css.font_awesome', 'URL', check_url,
#                 '//netdna.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css',
#                 'URL for the Font Awesome CSS file')
#
# register_option('display.notebook.js.datatables', 'URL', check_url,
#                 '//cdn.datatables.net/1.10.3/js/jquery.dataTables.min',
#                 'URL for the jQuery Datatables plugin Javascript file')
#
# register_option('display.notebook.js.swat', 'URL', check_url,
#                 '//www.sas.com/cas/python/js/swat',
#                 'URL for the SWAT Javascript file')
#
