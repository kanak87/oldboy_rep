package com.example.soma.cameraviewtest;

/**
 * Created by jihaeseong on 15. 11. 3..
 */
public class REQUEST{

    public String result;
    public String message;
    public String device_id;
    public String image;
    public String data;
    public detected_faces[] detected_faces;

    public class detected_faces{
        public int kind;
        public String name;
        public float probability;
        public int id;
        public int[] boundingbox;
        public String thumbnail;

        public detected_faces(){

        }
        public int getkind() {return kind;}

        public String getname() {return name;}

        public float getprobability() {return probability;}

        public int getfid() {return id;}

        public int[] getboundingbox() {return boundingbox;}

        public String getthumnail() {return thumbnail;}
    }
    //public detected_faces detected_f=new detected_faces();

    //public ArrayList<detected_faces> faces_list=new ArrayList<>();

    public REQUEST(){

    }
    public REQUEST(String id, String image){
        this.device_id=id;
        this.image=image;
    }

    //public int getkind() {return detected_f.kind;}
/*
    public String getname() {return detected_f.name;}

    public float getprobability() {return detected_f.probability;}

    public int getfid() {return detected_f.id;}

    public int[] getboundingbox() {return detected_f.boundingbox;}

    public String getthumnail() {return  detected_f.thumbnail;}
*/
    public String getResult() {return result;}

    public String getMessage() {return message;}

    public String getid() {return device_id;}

    public String getimg() {return image;}

    public String getdata() {return data;}

    public detected_faces[] getfaces() {return detected_faces;}

    public void setdata(String data) {this.data=data;}

    public void setid(String device_id) {this.device_id=device_id;}

    public void setimg(String img) {this.image=image;}

    //public detected_faces getDetected() { return detected_faces;}
}
