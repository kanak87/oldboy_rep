package com.example.soma.cameraviewtest.network;


import com.example.soma.cameraviewtest.REQUEST;

import retrofit.Callback;
import retrofit.http.Multipart;
import retrofit.http.POST;
import retrofit.http.Part;

public interface ServerInterface {

//    @Headers("Content-Type: multipart/form-data")
    //send picture recieve detected_picture
    @Multipart
    @POST("/request_face_detection")
    public void face_detection(@Part("data") String data, Callback<REQUEST> callback);
    //public void face_detection(@Body REQUEST request, Callback<REQUEST> callback);
/*
    // UUID 가 기존에 등록 되어 있는지 확인
    @POST("/request_data")
    public void face_data(String device_id, String img, Callback<REQUEST> callback);

    // UUID 가 기존에 등록 되어 있는지 확인
    @POST("/request_face_detection")
    public void face_detection(String device_id, String img, Callback<REQUEST> callback);
*/



}
