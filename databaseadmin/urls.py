from django.urls import path
from databaseadmin.views import NewsAddAPIView,SampleListView, SamplePostView, CycleAnalyteAPIView, CycleAddAnalyteAPIView, CycleUpdateAnalyteAPIView,SchemeAPIView, SchemeUpdateAPIView, SchemeDeleteAPIView, CycleAPIView, CyclePostAPIView, CycleUpdateAPIView, CycleDeleteAPIView,AnalytesByUnitAPIView,ParticipantSectorUpdateAPIView,ParticipantSectorCreateAPIView,ParticipantSectorListAPIView,ParticipantTypeUpdateAPIView,ParticipantTypeCreateAPIView,ParticipantTypeListAPIView,DesignationListAPIView,DesignationCreateAPIView,DesignationUpdateAPIView,DepartmentListAPIView,DepartmentCreateAPIView,DepartmentUpdateAPIView,DistrictListAPIView,DistrictCreateAPIView,DistrictUpdateAPIView,CityListAPIView,CityCreateAPIView,CityUpdateAPIView,AnalyteUpdateUnitsAPIView,AnalytesUnitsAPIView,AnalyteAddUnitsAPIView,AnalyteUpdateMethodsAPIView, AnalyteAddMethodsAPIView,AnalytesMethodsAPIView,AnalyteUpdateEquipmentsAPIView,AnalytesEquipmentsAPIView,AnalyteAddEquipmentsAPIView,AnalyteUpdateReagentsAPIView,AnalyteAddReagentsAPIView,AnalytesReagentsAPIView,AnalyteAddReagents,AnalytesListAPIView,MethodsPostAPIView,InstrumentsPostAPIView,InstrumentTypeCreateView,UnitsListAPIView,NewsListView,InstrumentsAPIView, InstrumentsUpdateAPIView, InstrumentTypeView,AnalyteUpdateAPIView, AnalyteAPIView, MethodsAPIView, UpdateInstrumentTypeView,  MethodsUpdateAPIView, UnitsAPIView, UnitsUpdateAPIView, ActivityLogDatabaseadmin, ReagentsListAPIView, ReagentsPostAPIView, ReagentsPutAPIView ,ManufacturalListAPIView, ManufacturalPostAPIView, ManufacturalPutAPIView

urlpatterns = [
    #Participant 
    path('participanttype_list/<id>',
         ParticipantTypeListAPIView.as_view(), name='participanttype_list'),
    path('participanttype_create',
         ParticipantTypeCreateAPIView.as_view(), name='participanttype_create'),
    path('participanttype_update/<id>',
        ParticipantTypeUpdateAPIView.as_view(), name='participanttype_update'),

    path('participantsector_list/<id>',
         ParticipantSectorListAPIView.as_view(), name='participantsector_list'),
    path('participantsector_create',
         ParticipantSectorCreateAPIView.as_view(), name='participantsector_create'),
    path('participantsector_update/<id>',
        ParticipantSectorUpdateAPIView.as_view(), name='participantsector_update'),

    path('city_list/<id>',
         CityListAPIView.as_view(), name='city_list'),
    path('city_create',
         CityCreateAPIView.as_view(), name='city_create'),
    path('city_update/<id>',
        CityUpdateAPIView.as_view(), name='city_update'),

    path('district_list/<id>',
         DistrictListAPIView.as_view(), name='district_list'),
    path('district_create',
         DistrictCreateAPIView.as_view(), name='district_create'),
    path('district_update/<id>',
        DistrictUpdateAPIView.as_view(), name='district_update'),

    path('department_list/<id>',
         DepartmentListAPIView.as_view(), name='department_list'),
    path('department_create',
         DepartmentCreateAPIView.as_view(), name='department_create'),
    path('department_update/<id>',
        DepartmentUpdateAPIView.as_view(), name='department_update'),

    path('designation_list/<id>',
         DesignationListAPIView.as_view(), name='designation_list'),
    path('designation_create',
         DesignationCreateAPIView.as_view(), name='designation_create'),
    path('designation_update/<id>',
        DesignationUpdateAPIView.as_view(), name='designation_update'),
    
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
    path('news-list/<id>',
         NewsListView.as_view(), name='news-list'),
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
    path('sample-list/<id>',
         SampleListView.as_view(), name='sample-list'),
    path('post-sample',
         SamplePostView.as_view(), name='post-sample'),
    # path('news-list-participant/<id>',
    #      NewsListViewParticipant.as_view(), name='news-list-participantt'),
    path('news-add',
         NewsAddAPIView.as_view(), name='news-add'),

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
         
    # Cycle Analytes
    path('cycle-analyte-list/<id>',
         CycleAnalyteAPIView.as_view(), name='cycle-analyte-list'),     
    path('cycle-add-analyte/<id>',
        CycleAddAnalyteAPIView.as_view(), name='cycle-add-analyte'),
    path('cycle-update-analyte/<id>',
         CycleUpdateAnalyteAPIView.as_view(), name='cycle-update-analyte'),
     #Analytes assocaited with unit
     path('analyte-units/<id>',
         AnalytesByUnitAPIView.as_view(), name='analyte-units'),    
]