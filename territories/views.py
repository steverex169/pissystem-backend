from django.shortcuts import render
from cgi import test
import codecs
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import redirect
from rest_framework.views import APIView
from territories.models import Territories
from territories.serializers import TerritoriesSerializer
import csv
import pandas as pd


# Api for post and delete cities: By the running this Api deleting all the items associated with it if already that Api (Post, Delete) in running state one time no need to run again and again..
# If you want to add any new City, then it has to be entered through the portl of master admin (labhazirapi.com). and if it is csv file you have made with proper SOP's, run the post ai through postman,


class TerritoriesListView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        file=request.FILES.get("file")
        reader=csv.DictReader(codecs.iterdecode(file,"utf-8"), delimiter=",")
        data=list(reader)
        serializer_class = TerritoriesSerializer(data=data, many=True)
        if serializer_class.is_valid():
                serializer_class.save()
        territories_list=[]
        for row in serializer_class.data:
            territories_list.append(
                 Territories(
                    province=row["province"],
                    city=row["city"],
                    district=row["district"],
                    office=row["office"]
                    )   
                ) 
        Territories.objects.bulk_create(territories_list)
        return Response({"status": status.HTTP_200_OK, "message":serializer_class.data})
   
    # Delete request to delete data of the All territories data
    # def delete(self, request, *args, **kwargs):
    #     try:
    #         Territories.objects.all().delete()
    #         return Response({"status": status.HTTP_200_OK, "message": "Deleted successfully"})

    #     except Territories.DoesNotExist:
    #         return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "Sorry! No such record to delete."})

class TerritoriesDitrictCityListView(APIView):
    permission_classes = (AllowAny,)

    # Get request to get data of the Tests to get all of the test list
    def get(self, request, *args, **kwargs):
        try:
            CityDistrict_list = Territories.objects.all()
            serializer_class = TerritoriesSerializer(CityDistrict_list, many=True)
            return Response({"status": status.HTTP_200_OK, "data": serializer_class.data})
        except Territories.DoesNotExist:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": "No District City List exist"})
