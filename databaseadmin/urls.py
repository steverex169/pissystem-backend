from django.urls import path
from databaseadmin.views import NewsListView,InstrumentsAPIView, InstrumentsUpdateAPIView, InstrumentTypeView,AnalyteUpdateAPIView, AnalyteAPIView, MethodsAPIView, MethodsUpdateAPIView, SchemeAPIView, SchemeUpdateAPIView, SchemeDeleteAPIView, CycleAPIView, CyclePostAPIView, CycleUpdateAPIView, CycleDeleteAPIView, UpdateInstrumentTypeView, UnitsAPIView, UnitsListAPIView, UnitsUpdateAPIView, ActivityLogDatabaseadmin, ReagentsListAPIView, ReagentsPostAPIView, ReagentsPutAPIView ,ManufacturalListAPIView, ManufacturalPostAPIView, ManufacturalPutAPIView, SampleListView, SamplePostView, CycleAnalyteAPIView, CycleAddAnalyteAPIView, CycleUpdateAnalyteAPIView

urlpatterns = [
    path('units_update/<id>', UnitsUpdateAPIView.as_view(), name='units_update'),
    path('units_create', UnitsAPIView.as_view(), name='units_create'),
    path('units_list', UnitsListAPIView.as_view(), name='units_list'),
    path('history_list/<id>', ActivityLogDatabaseadmin.as_view(), name='history_list'),
    path('reagent_update/<id>', ReagentsPutAPIView.as_view(), name='reagent_update'),
    path('reagent_create', ReagentsPostAPIView.as_view(), name='reagent_create'),
    path('reagent_list', ReagentsListAPIView.as_view(), name='reagent_list'), 
    path('manufactural_update/<id>', ManufacturalPutAPIView.as_view(), name='manufactural_update'),
    path('manufactural_create', ManufacturalPostAPIView.as_view(), name='manufactural_create'),
    path('manufactural_list', ManufacturalListAPIView.as_view(), name='manufactural_list'), 
        path('instrument-type-list',
         InstrumentTypeView.as_view(), name='instrument-type-list'),
    path('update-instrument-type-list/<id>',
        UpdateInstrumentTypeView.as_view(), name='update-instrument-type-list'),
    path('methods-list',
         MethodsAPIView.as_view(), name='methods-list'),
    path('update-method-list/<id>',
        MethodsUpdateAPIView.as_view(), name='update-method-list'), 
    path('scheme-list',
        SchemeAPIView.as_view(), name='scheme-list'),
    path('update-scheme/<id>',
        SchemeUpdateAPIView.as_view(), name='update-scheme/<id>'),   
    path('delete-scheme/<id>',
        SchemeDeleteAPIView.as_view(), name='delete-scheme/<id>'),
    path('cycle-list/<id>',
         CycleAPIView.as_view(), name='cycle-list/<id>'),
    path('post-cycle',
        CyclePostAPIView.as_view(), name='post-cycle'),
    path('update-cycle-list/<id>',
        CycleUpdateAPIView.as_view(), name='update-cycle-list/<id>'),  
    path('delete-cycle/<id>',
        CycleDeleteAPIView.as_view(), name='delete-cycle/<id>'), 
    path('analyte-list',
        AnalyteAPIView.as_view(), name='analyte-list'),
    path('update-analyte/<id>',
        AnalyteUpdateAPIView.as_view(), name='update-analyte'),
    path('instrument-list',
         InstrumentsAPIView.as_view(), name='instrument-list'),
    path('update-instrument-list/<id>',
        InstrumentsUpdateAPIView.as_view(), name='update-instrument-list'),
    path('news-list',
         NewsListView.as_view(), name='news-list'),
    path('sample-list/<id>',
         SampleListView.as_view(), name='sample-list'),
    path('post-sample',
         SamplePostView.as_view(), name='post-sample'),

    
    # Cycle Analytes
    path('cycle-analyte-list/<id>',
         CycleAnalyteAPIView.as_view(), name='cycle-analyte-list'),     
    path('cycle-add-analyte/<id>',
        CycleAddAnalyteAPIView.as_view(), name='cycle-add-analyte'),
    path('cycle-update-analyte/<id>',
         CycleUpdateAnalyteAPIView.as_view(), name='cycle-update-analyte'),
]