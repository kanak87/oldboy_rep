package com.example.soma.cameraviewtest;

import java.util.ArrayList;

/**
 * Created by jihaeseong on 15. 11. 3..
 */
public class data {
    public String result;
    public String message;
    public String device_id;
    public String img;
    public class detected_faces{
        public String id;
        public String name;
        public int probability;
        public int[] boundingbox;
        public String thumbnail;

        public detected_faces(){

        }
    }
    public ArrayList<detected_faces> faces_list;

    public data(){
    }
    public data(String id, String img){
        this.device_id=id;
        this.img=img;
    }
    public String getResult() {return result;}

    public String getMessage() {return message;}

    public String getid() {return device_id;}

    public String getimg() {return img;}

    public void setid(String device_id) {this.device_id=device_id;}

    public void setimg(String img) {this.img=img;}

    public detected_faces getDetected(int index) { return faces_list.get(index);}

}
