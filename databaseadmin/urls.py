from django.urls import path
from databaseadmin.views import SchemeUpdateAnalyteAPIView, InstrumentTypefileView,ProvinceUpdateAPIView,ProvinceCreateAPIView, ProvinceListAPIView,DeleteMAnufacturerView,ReagentsInManufacturerAPIView,InstrumentsInManufacturerAPIView,DeleteInstrumentView,AnalytesByInstrumentAPIView,DeleteReagentView,AnalytesByReagentAPIView,CountryUpdateAPIView,CountryCreateAPIView,CountryListAPIView,DeleteAnalyteView,DeleteMethodView,AnalytesByMethodAPIView,DeleteInstrumentTypeView,InstrumentAndInstrumentTypeAPIView, NewsAddAPIView,SampleListView, SamplePostView, SchemeAPIView, SchemeUpdateAPIView, SchemeDeleteAPIView, CycleAPIView, CyclePostAPIView, CycleUpdateAPIView, CycleDeleteAPIView,AnalytesByUnitAPIView,ParticipantSectorUpdateAPIView,ParticipantSectorCreateAPIView,ParticipantSectorListAPIView,ParticipantTypeUpdateAPIView,ParticipantTypeCreateAPIView,ParticipantTypeListAPIView,DesignationListAPIView,DesignationCreateAPIView,DesignationUpdateAPIView,DepartmentListAPIView,DepartmentCreateAPIView,DepartmentUpdateAPIView,DistrictListAPIView,DistrictCreateAPIView,DistrictUpdateAPIView,CityListAPIView,CityCreateAPIView,CityUpdateAPIView,AnalyteUpdateUnitsAPIView,AnalytesUnitsAPIView,AnalyteAddUnitsAPIView,AnalyteUpdateMethodsAPIView, AnalyteAddMethodsAPIView,AnalytesMethodsAPIView,AnalyteUpdateEquipmentsAPIView,AnalytesEquipmentsAPIView,AnalyteAddEquipmentsAPIView,AnalyteUpdateReagentsAPIView,AnalyteAddReagentsAPIView,AnalytesReagentsAPIView,AnalyteAddReagents,AnalytesListAPIView,MethodsPostAPIView,InstrumentsPostAPIView,InstrumentTypeCreateView,UnitsListAPIView,NewsListView,InstrumentsAPIView, InstrumentsUpdateAPIView, InstrumentTypeView,AnalyteUpdateAPIView, AnalyteAPIView, MethodsAPIView, UpdateInstrumentTypeView,  MethodsUpdateAPIView, UnitsAPIView, UnitsUpdateAPIView, ActivityLogDatabaseadmin, ReagentsListAPIView, ReagentsPostAPIView,SchemePostAPIView,SchemeAnalyteAPIView,SchemeAddAnalyteAPIView, ReagentsPutAPIView ,ManufacturalListAPIView, ManufacturalPostAPIView, ManufacturalPutAPIView

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

    path('country_list/<id>',
         CountryListAPIView.as_view(), name='country_list'),
    path('country_create',
         CountryCreateAPIView.as_view(), name='country_create'),
    path('country_update/<id>',
        CountryUpdateAPIView.as_view(), name='country_update'),

    path('province_list/<id>',
         ProvinceListAPIView.as_view(), name='province_list'),
    path('province_create',
         ProvinceCreateAPIView.as_view(), name='province_create'),
    path('province_update/<id>',
        ProvinceUpdateAPIView.as_view(), name='province_update'),

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
    path('delete-reagent/<id>',
         DeleteReagentView.as_view(), name='delete-reagent'),
    path('manufactural_update/<id>', ManufacturalPutAPIView.as_view(), name='manufactural_update'),
    path('manufactural_create', ManufacturalPostAPIView.as_view(), name='manufactural_create'),
    path('manufactural_list/<id>', ManufacturalListAPIView.as_view(), name='manufactural_list'),
    path('delete-manufacturer/<id>',
         DeleteMAnufacturerView.as_view(), name='delete-manufacturer'),
    path('instrument-type-list/<id>',InstrumentTypeView.as_view(), name='instrument-type-list'),
    path('instrument-type-create-list',InstrumentTypeCreateView.as_view(), name='instrument-type-create-list'),
    path('update-instrument-type-list/<id>',
        UpdateInstrumentTypeView.as_view(), name='update-instrument-type-list'),
    path('delete-instrumenttype/<id>',
         DeleteInstrumentTypeView.as_view(), name='delete-instrumenttype'),
    path('methods-list/<id>',
         MethodsAPIView.as_view(), name='methods-list'),
    path('methods-create-list',
         MethodsPostAPIView.as_view(), name='methods-create-list'),
    path('update-method-list/<id>',
        MethodsUpdateAPIView.as_view(), name='update-method-list'),
     path('delete-method/<id>',
         DeleteMethodView.as_view(), name='delete-method'),

    path('analyte-add-reagent',
        AnalyteAddReagents.as_view(), name='analyte-add-reagent'),
    path('analyte-create-list',
        AnalyteAPIView.as_view(), name='analyte-create-list'),
    path('analyte-list/<id>',
        AnalytesListAPIView.as_view(), name='analyte-list'),
    path('update-analyte/<id>',
        AnalyteUpdateAPIView.as_view(), name='update-analyte'),
     path('delete-analyte/<id>',
         DeleteAnalyteView.as_view(), name='delete-analyte'),

    path('instrument-list/<id>',
         InstrumentsAPIView.as_view(), name='instrument-list'),
    path('instrument-create',
         InstrumentsPostAPIView.as_view(), name='instrument-create'),     
    path('update-instrument-list/<id>',
        InstrumentsUpdateAPIView.as_view(), name='update-instrument-list'),
    
     path('delete-instrument/<id>',
         DeleteInstrumentView.as_view(), name='delete-instrument'),

    path('scheme-list/<id>',
        SchemeAPIView.as_view(), name='scheme-list'),
    path('scheme-list',
        SchemePostAPIView.as_view(), name='scheme-list'),
    path('update-scheme/<id>',
        SchemeUpdateAPIView.as_view(), name='update-scheme'),   
    path('delete-scheme/<id>',
        SchemeDeleteAPIView.as_view(), name='delete-scheme'),
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
         
     #Analytes assocaited with unit
     path('analyte-units/<id>',
         AnalytesByUnitAPIView.as_view(), name='analyte-units'),  
     path('instrument-type-file',
         InstrumentTypefileView.as_view(), name='instrument-type-file'),  

     #Analytes assocaited with reagent
     path('analyte-reagents/<id>',
         AnalytesByReagentAPIView.as_view(), name='analyte-reagents'),  

     #Analytes assocaited with method
     path('analyte-methods/<id>',
         AnalytesByMethodAPIView.as_view(), name='analyte-methods'),   

     #Analytes assocaited with instrument
     path('analyte-instruments/<id>',
         AnalytesByInstrumentAPIView.as_view(), name='analyte-instruments'),    

     path('instrument-instrumenttype/<id>',
         InstrumentAndInstrumentTypeAPIView.as_view(), name='instrument-instrumenttype'),  
         
     path('instrument-manufacturer/<id>',
         InstrumentsInManufacturerAPIView.as_view(), name='instrument-manufacturer'),  
         
     path('reagent-manufacturer/<id>',
         ReagentsInManufacturerAPIView.as_view(), name='reagent-manufacturer'),  
     
    # Scheme Analytes
    path('scheme-analyte-list/<id>',
         SchemeAnalyteAPIView.as_view(), name='scheme-analyte-list'),     
    path('scheme-add-analyte/<id>',
        SchemeAddAnalyteAPIView.as_view(), name='scheme-add-analyte'),
    path('scheme-update-analyte/<id>',
         SchemeUpdateAnalyteAPIView.as_view(), name='scheme-update-analyte'),

     #Analytes assocaited with unit
     path('analyte-units/<id>',
         AnalytesByUnitAPIView.as_view(), name='analyte-units'),  

     #Analytes assocaited with reagent
     path('analyte-reagents/<id>',
         AnalytesByReagentAPIView.as_view(), name='analyte-reagents'),  

     #Analytes assocaited with method
     path('analyte-methods/<id>',
         AnalytesByMethodAPIView.as_view(), name='analyte-methods'),   

     #Analytes assocaited with instrument
     path('analyte-instruments/<id>',
         AnalytesByInstrumentAPIView.as_view(), name='analyte-instruments'),    

     path('instrument-instrumenttype/<id>',
         InstrumentAndInstrumentTypeAPIView.as_view(), name='instrument-instrumenttype'),  
         
     path('instrument-manufacturer/<id>',
         InstrumentsInManufacturerAPIView.as_view(), name='instrument-manufacturer'),  
         
     path('reagent-manufacturer/<id>',
         ReagentsInManufacturerAPIView.as_view(), name='reagent-manufacturer'),  

   #news      
    path('news-list/<id>',
         NewsListView.as_view(), name='news-list'),
    path('news-add',
         NewsAddAPIView.as_view(), name='news-add'),  
]
