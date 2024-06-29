from django.urls import path
from databaseadmin.views import AnalyteUpdateUnitsAPIView,AnalytesUnitsAPIView,AnalyteAddUnitsAPIView,AnalyteUpdateMethodsAPIView, AnalyteAddMethodsAPIView,AnalytesMethodsAPIView,AnalyteUpdateEquipmentsAPIView,AnalytesEquipmentsAPIView,AnalyteAddEquipmentsAPIView,AnalyteUpdateReagentsAPIView,AnalyteAddReagentsAPIView,AnalytesReagentsAPIView,AnalyteAddReagents,AnalytesListAPIView,MethodsPostAPIView,InstrumentsPostAPIView,InstrumentTypeCreateView,UnitsListAPIView,NewsListView,InstrumentsAPIView, InstrumentsUpdateAPIView, InstrumentTypeView,AnalyteUpdateAPIView, AnalyteAPIView, MethodsAPIView, UpdateInstrumentTypeView,  MethodsUpdateAPIView, UnitsAPIView, UnitsUpdateAPIView, ActivityLogDatabaseadmin, ReagentsListAPIView, ReagentsPostAPIView, ReagentsPutAPIView ,ManufacturalListAPIView, ManufacturalPostAPIView, ManufacturalPutAPIView

urlpatterns = [
    path('units_update/<id>', UnitsUpdateAPIView.as_view(), name='units_update'),
    path('units_create', UnitsAPIView.as_view(), name='units_create'),
    path('units_list/<id>', UnitsListAPIView.as_view(), name='units_list'),
    path('history_list/<id>', ActivityLogDatabaseadmin.as_view(), name='history_list'),
    path('reagent_update/<id>', ReagentsPutAPIView.as_view(), name='reagent_update'),
    path('reagent_create', ReagentsPostAPIView.as_view(), name='reagent_create'),
    path('reagent_list/<id>', ReagentsListAPIView.as_view(), name='reagent_list'), 
    path('manufactural_update/<id>', ManufacturalPutAPIView.as_view(), name='manufactural_update'),
    path('manufactural_create', ManufacturalPostAPIView.as_view(), name='manufactural_create'),
    path('manufactural_list/<id>', ManufacturalListAPIView.as_view(), name='manufactural_list'),
    path('instrument-type-list/<id>',InstrumentTypeView.as_view(), name='instrument-type-list'),

    path('instrument-type-create-list',InstrumentTypeCreateView.as_view(), name='instrument-type-create-list'),
    path('update-instrument-type-list/<id>',
        UpdateInstrumentTypeView.as_view(), name='update-instrument-type-list'),
    path('methods-list/<id>',
         MethodsAPIView.as_view(), name='methods-list'),
    path('methods-create-list',
         MethodsPostAPIView.as_view(), name='methods-create-list'),
    path('update-method-list/<id>',
        MethodsUpdateAPIView.as_view(), name='update-method-list'),
    path('analyte-add-reagent',
        AnalyteAddReagents.as_view(), name='analyte-add-reagent'),
    path('analyte-create-list',
        AnalyteAPIView.as_view(), name='analyte-create-list'),
    path('analyte-list/<id>',
        AnalytesListAPIView.as_view(), name='analyte-list'),
    path('update-analyte/<id>',
        AnalyteUpdateAPIView.as_view(), name='update-analyte'),
    path('instrument-list/<id>',
         InstrumentsAPIView.as_view(), name='instrument-list'),
    path('instrument-create',
         InstrumentsPostAPIView.as_view(), name='instrument-create'),     
    path('update-instrument-list/<id>',
        InstrumentsUpdateAPIView.as_view(), name='update-instrument-list'),
    path('news-list',
         NewsListView.as_view(), name='news-list'),

    #analyte adding reagents
     path('analyte-reagents-list/<id>',
         AnalytesReagentsAPIView.as_view(), name='analyte-reagents-list'),     
    path('analyte-add-reagent/<id>',
        AnalyteAddReagentsAPIView.as_view(), name='analyte-add-reagent'),
    path('analyte-update-reagent/<id>',
         AnalyteUpdateReagentsAPIView.as_view(), name='analyte-update-reagent'),


    #analyte adding equipments
     path('analyte-equipments-list/<id>',
         AnalytesEquipmentsAPIView.as_view(), name='analyte-equipments-list'),     
    path('analyte-add-equipments/<id>',
        AnalyteAddEquipmentsAPIView.as_view(), name='analyte-add-equipments'),
    path('analyte-update-equipments/<id>',
         AnalyteUpdateEquipmentsAPIView.as_view(), name='analyte-update-equipments'),

    #analyte adding methods
     path('analyte-methods-list/<id>',
         AnalytesMethodsAPIView.as_view(), name='analyte-methods-list'),     
    path('analyte-add-methods/<id>',
        AnalyteAddMethodsAPIView.as_view(), name='analyte-add-methods'),
    path('analyte-update-methods/<id>',
         AnalyteUpdateMethodsAPIView.as_view(), name='analyte-update-methods'),

    #analyte adding units
     path('analyte-units-list/<id>',
         AnalytesUnitsAPIView.as_view(), name='analyte-units-list'),     
    path('analyte-add-units/<id>',
        AnalyteAddUnitsAPIView.as_view(), name='analyte-add-units'),
    path('analyte-update-units/<id>',
         AnalyteUpdateUnitsAPIView.as_view(), name='analyte-update-units'),
]