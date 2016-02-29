from django.conf.urls import *
from corehq.apps.export.views import (
    CreateCustomFormExportView,
    CreateCustomCaseExportView,
    CreateNewCustomFormExportView,
    CreateNewCustomCaseExportView,
    EditCustomFormExportView,
    EditCustomCaseExportView,
    EditNewCustomFormExportView,
    EditNewCustomCaseExportView,
    DeleteCustomExportView,
    DeleteNewCustomExportView,
    DownloadFormExportView,
    DownloadCaseExportView,
    FormExportListView,
    CaseExportListView,
    BulkDownloadFormExportView,
    DeIdFormExportListView,
    DownloadNewFormExportView, BulkDownloadNewFormExportView)

urlpatterns = patterns(
    'corehq.apps.export.views',
    url(r"^custom/form/$",
        FormExportListView.as_view(),
        name=FormExportListView.urlname),
    url(r"^custom/form_deid/$",
        DeIdFormExportListView.as_view(),
        name=DeIdFormExportListView.urlname),
    url(r"^custom/case/$",
        CaseExportListView.as_view(),
        name=CaseExportListView.urlname),
    url(r"^custom/form/create$",
        CreateCustomFormExportView.as_view(),
        name=CreateCustomFormExportView.urlname),
    url(r"^custom/case/create$",
        CreateCustomCaseExportView.as_view(),
        name=CreateCustomCaseExportView.urlname),
    url(r"^custom/new/form/create$",
        CreateNewCustomFormExportView.as_view(),
        name=CreateNewCustomFormExportView.urlname),
    url(r"^custom/new/case/create$",
        CreateNewCustomCaseExportView.as_view(),
        name=CreateNewCustomCaseExportView.urlname),
    url(r"^custom/form/download/bulk/$",
        BulkDownloadFormExportView.as_view(),
        name=BulkDownloadFormExportView.urlname),
    url(r"^custom/new/form/download/bulk/$",
        BulkDownloadNewFormExportView.as_view(),
        name=BulkDownloadNewFormExportView.urlname),
    url(r"^custom/form/download/(?P<export_id>[\w\-]+)/$",
        DownloadFormExportView.as_view(),
        name=DownloadFormExportView.urlname),
    url(r"^custom/new/form/download/(?P<export_id>[\w\-]+)/$",
        DownloadNewFormExportView.as_view(),
        name=DownloadNewFormExportView.urlname),
    url(r"^custom/new/form/edit/(?P<export_id>[\w\-]+)/$",
        EditNewCustomFormExportView.as_view(),
        name=EditNewCustomFormExportView.urlname),
    url(r"^custom/new/case/edit/(?P<export_id>[\w\-]+)/$",
        EditNewCustomCaseExportView.as_view(),
        name=EditNewCustomCaseExportView.urlname),
    url(r"^custom/form/edit/(?P<export_id>[\w\-]+)/$",
        EditCustomFormExportView.as_view(),
        name=EditCustomFormExportView.urlname),
    url(r"^custom/case/download/(?P<export_id>[\w\-]+)/$",
        DownloadCaseExportView.as_view(),
        name=DownloadCaseExportView.urlname),
    url(r"^custom/case/edit/(?P<export_id>[\w\-]+)/$",
        EditCustomCaseExportView.as_view(),
        name=EditCustomCaseExportView.urlname),
    url(r"^custom/delete/(?P<export_id>[\w\-]+)/$",
        DeleteCustomExportView.as_view(),
        name=DeleteCustomExportView.urlname),
    url(r"^custom/new/(?P<export_type>[\w\-]+)/delete/(?P<export_id>[\w\-]+)/$",
        DeleteNewCustomExportView.as_view(),
        name=DeleteNewCustomExportView.urlname),
)
