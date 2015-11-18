package com.example.soma.cameraviewtest;

import android.app.ActionBar;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.res.Configuration;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.PixelFormat;
import android.graphics.drawable.BitmapDrawable;
import android.hardware.Camera;
import android.media.AudioManager;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.os.StrictMode;
import android.provider.MediaStore;
import android.support.v7.app.AppCompatActivity;
import android.util.Base64;
import android.util.Log;
import android.view.Surface;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.example.soma.cameraviewtest.network.ApplicationController;
import com.example.soma.cameraviewtest.network.ServerInterface;
import com.example.soma.cameraviewtest.uuid.MyUUID;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;

import retrofit.Callback;
import retrofit.RetrofitError;
import retrofit.client.Response;

public class MainActivity extends AppCompatActivity implements SurfaceHolder.Callback{

    Camera camera;
    ImageButton photo;
    ImageView imageview;
    TextView detect_text;
    SurfaceView surfaceView;
    SurfaceHolder surfaceHolder;
    boolean previewing = false;;
    int count=0;
    String uuid="";
    private ServerInterface api;
    String imagecode;
    String filePath;
    Bitmap thumbnail_decode;
    LinearLayout scroll_layout;
    int rotation_count=0;
    BitmapDrawable imageView_draw;
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if(android.os.Build.VERSION.SDK_INT > 9) {

            StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();

            StrictMode.setThreadPolicy(policy);

        }

        uuid = new MyUUID().getUUID(getApplicationContext());
        ApplicationController application = ApplicationController.getInstance();
        application.buildServerInterface("175.126.82.175", 20100);
        api = ApplicationController.getInstance().getServerInterface();

        Button buttonStartCameraPreview = (Button)findViewById(R.id.startcamerapreview);
        Button buttonStopCameraPreview = (Button)findViewById(R.id.stopcamerapreview);
        photo = (ImageButton) findViewById(R.id.imageButton);
        imageview = (ImageView) findViewById(R.id.imageView);
        scroll_layout = (LinearLayout)findViewById(R.id.scroll_layout);

        getWindow().setFormat(PixelFormat.UNKNOWN);
        surfaceView = (SurfaceView)findViewById(R.id.surfaceview);
        surfaceHolder = surfaceView.getHolder();
        surfaceHolder.addCallback(this);
        surfaceHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);
        final Context mContext=this;
        buttonStartCameraPreview.setOnClickListener(new Button.OnClickListener(){

            @Override
            public void onClick(View v) {
                // TODO Auto-generated method stub
                if(!previewing){
                    camera = Camera.open(Camera.CameraInfo.CAMERA_FACING_FRONT);
                    imageview.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 0));
                    surfaceView.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 2));
                    setCameraDisplayOrientation((Activity) mContext, Camera.CameraInfo.CAMERA_FACING_FRONT, camera);
                    if (camera != null){
                        try {
                            camera.setPreviewDisplay(surfaceHolder);
                            camera.setDisplayOrientation(90);
                            Camera.Parameters params = null;
                            camera.startPreview();
                            //camera.setFaceDetectionListener(new MyFaceDetectionListener());
                            //camera.startFaceDetection();

                            previewing = true;
                        } catch (IOException e) {
                            // TODO Auto-generated catch block
                            e.printStackTrace();
                        }
                    }
                }
            }});

        buttonStopCameraPreview.setOnClickListener(new Button.OnClickListener(){

            @Override
            public void onClick(View v) {
                // TODO Auto-generated method stub
                if(camera != null && previewing){
                    camera.stopPreview();
                    camera.release();
                    camera = null;

                    previewing = false;
                }
            }
        });

        surfaceView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(camera!=null)
                    camera.takePicture(shutterCallback, rawCallback, jpegCallback);
            }
        });

        imageview.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                int screenWidth = getResources().getDisplayMetrics().widthPixels;
                int screenHeight = getResources().getDisplayMetrics().heightPixels;
                imageView_draw = (BitmapDrawable)((ImageView) findViewById(R.id.imageView)).getDrawable();
                Bitmap bm = imageView_draw.getBitmap();
/*
                if (getResources().getConfiguration().orientation == Configuration.ORIENTATION_PORTRAIT) {
                    // Notice that width and height are reversed
                    Bitmap scaled = Bitmap.createScaledBitmap(bm, bm.getHeight(), bm.getWidth(), true);
                    int w = scaled.getWidth();
                    int h = scaled.getHeight();
                    // Setting post rotate to 90
                    Matrix mtx = new Matrix();
                    mtx.postRotate(0);
                    // Rotating Bitmap
                    bm = Bitmap.createBitmap(scaled, 0, 0, w, h, mtx, true);
                } else {// LANDSCAPE MODE
                    //No need to reverse width and height
                    Bitmap scaled = Bitmap.createScaledBitmap(bm, bm.getWidth(), bm.getHeight(), true);
                    bm = scaled;
                }
                */
                ByteArrayOutputStream bos = new ByteArrayOutputStream();
                bm.compress(Bitmap.CompressFormat.JPEG, 100, bos); //저장된이미지를 jpeg로 포맷 품질100으로하여 출력
                byte[] ba = bos.toByteArray();
                imagecode = Base64.encodeToString(ba, Base64.DEFAULT);

                //Log.v("base64", String.valueOf(imagecode.length()));
                detect_thumbnail(imagecode);
                imageview.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 0));
                surfaceView.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 2));
                rotation_count=0;
            }
        });

        imageview.setOnLongClickListener(new View.OnLongClickListener() {
            @Override
            public boolean onLongClick(View v) {
                Bitmap bitmap = BitmapFactory.decodeFile(filePath);
                imageView_draw = (BitmapDrawable)((ImageView) findViewById(R.id.imageView)).getDrawable();
                Bitmap bm = imageView_draw.getBitmap();

                if (getResources().getConfiguration().orientation == Configuration.ORIENTATION_PORTRAIT) {
                    // Notice that width and height are reversed
                    Bitmap scaled = null;

                    if(rotation_count!=0) {
                        Log.v("rotate_test", "0 "+bitmap.getHeight()+" "+bitmap.getWidth());
                        scaled = Bitmap.createScaledBitmap(bm, bitmap.getHeight(), bitmap.getWidth(), true);
                        rotation_count=0;
                    }
                    else if(bitmap.getWidth()>=bitmap.getHeight()){
                        Log.v("rotate_test", "1 "+bitmap.getHeight()+" "+bitmap.getWidth());
                        scaled = Bitmap.createScaledBitmap(bm, bitmap.getWidth(), bitmap.getHeight(), true);
                        rotation_count++;
                    }
                    int w = scaled.getWidth();
                    int h = scaled.getHeight();
                    // Setting post rotate to 90
                    Matrix mtx = new Matrix();
                    mtx.postRotate(90);
                    // Rotating Bitmap
                    bm = Bitmap.createBitmap(scaled, 0, 0, w, h, mtx, true);
                } else {// LANDSCAPE MODE
                    //No need to reverse width and height
                    Bitmap scaled = Bitmap.createScaledBitmap(bm, bm.getWidth(), bm.getHeight(), true);
                    bm = scaled;
                }
                imageview.setImageBitmap(bm);

                return true;
            }
        });
        photo.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(Intent.ACTION_PICK);
                intent.setType(MediaStore.Images.Media.CONTENT_TYPE);
                intent.setData(MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
                startActivityForResult(intent, REQUEST_PHOTO_ALBOM);
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode,resultCode,data);

        try {
            if(requestCode == REQUEST_PHOTO_ALBOM) {
                Uri uri = getRealPathUri(data.getData());
                filePath = uri.toString();
                Bitmap bitmap = BitmapFactory.decodeFile(filePath);
                imageview.setImageBitmap(bitmap);
                imageview.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 2));
                surfaceView.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 0));
                camera.stopPreview();
                camera.release();
                camera = null;

                previewing = false;
            }
        }   catch(Exception e){
            Log.e("photo", "Error : " + e);
        }
    }

    private Uri getRealPathUri(Uri uri) {
        Uri filePathUri = uri;
        if(uri.getScheme().toString().compareTo("content")==0){
            Cursor cursor = getApplicationContext().getContentResolver().query(uri, null, null, null, null);
            if(cursor.moveToFirst()){
                int column_index=cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA);
                filePathUri = Uri.parse(cursor.getString(column_index));
            }
        }
        return filePathUri;
    }
/*
    class MyFaceDetectionListener implements Camera.FaceDetectionListener {

        @Override
        public void onFaceDetection(Camera.Face[] faces, Camera camera) {
            if (faces.length > 0){
                Log.v("detect", count + "");
                count++;
                if(count%100==0) {
                    //take picture
//                    camera.setDisplayOrientation(180);
                    //camera.stopPreview();
                    camera.takePicture(shutterCallback, rawCallback, jpegCallback);
                    //camera.setDisplayOrientation(90);

                    //img change

                }
            }
            else {
                detect_text.setText("detect : 0");
            }
        }
    }
*/
    Camera.ShutterCallback shutterCallback = new Camera.ShutterCallback() {
        public void onShutter() {
            //			 Log.d(TAG, "onShutter'd");
            AudioManager mgr = (AudioManager) getSystemService(Context.AUDIO_SERVICE);
            mgr.playSoundEffect(AudioManager.FLAG_PLAY_SOUND);
        }
    };

    Camera.PictureCallback rawCallback = new Camera.PictureCallback() {
        public void onPictureTaken(byte[] data, Camera camera) {
            //			 Log.d(TAG, "onPictureTaken - raw");
        }
    };

    Camera.PictureCallback jpegCallback = new Camera.PictureCallback() {
        public void onPictureTaken(byte[] data, Camera camera) {
            camera.stopPreview();
            new SaveImageTask().execute(data);
            camera.startPreview();

            if (data != null) {
                int screenWidth = getResources().getDisplayMetrics().widthPixels;
                int screenHeight = getResources().getDisplayMetrics().heightPixels;
                Bitmap bm = BitmapFactory.decodeFile("/storage/emulated/0/camtest/detect.jpg");

                if (getResources().getConfiguration().orientation == Configuration.ORIENTATION_PORTRAIT) {
                    // Notice that width and height are reversed
                    Bitmap scaled = Bitmap.createScaledBitmap(bm, screenHeight, screenWidth, true);
                    int w = scaled.getWidth();
                    int h = scaled.getHeight();
                    // Setting post rotate to 90
                    Matrix mtx = new Matrix();
                    mtx.postRotate(270);
                    // Rotating Bitmap
                    bm = Bitmap.createBitmap(scaled, 0, 0, w, h, mtx, true);
                }else{// LANDSCAPE MODE
                    //No need to reverse width and height
                    Bitmap scaled = Bitmap.createScaledBitmap(bm, screenWidth, screenHeight , true);
                    bm=scaled;
                }
                ByteArrayOutputStream bos = new ByteArrayOutputStream();
                bm.compress(Bitmap.CompressFormat.JPEG, 100, bos); //저장된이미지를 jpeg로 포맷 품질100으로하여 출력
                byte[] ba = bos.toByteArray();
                imagecode= Base64.encodeToString(ba, Base64.DEFAULT);
                Log.v("api_all+", imagecode.toString());
            }
/*
            Bitmap bm = BitmapFactory.decodeFile("/storage/emulated/0/camtest/detect.jpg");
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            bm.compress(Bitmap.CompressFormat.JPEG, 100, bos); //저장된이미지를 jpeg로 포맷 품질100으로하여 출력
            byte[] ba = bos.toByteArray();
            imagecode= Base64.encodeToString(ba, Base64.DEFAULT);
*/
            //Log.v("base64", String.valueOf(imagecode.length()));
            detect_thumbnail(imagecode);

            Log.d("picture", "onPictureTaken - jpeg");
        }
    };
    @Override
    public void surfaceChanged(SurfaceHolder holder, int format, int width,
                               int height) {
        // TODO Auto-generated method stub

    }

    @Override
    public void surfaceCreated(SurfaceHolder holder) {
        // TODO Auto-generated method stub

    }

    @Override
    public void surfaceDestroyed(SurfaceHolder holder) {
        // TODO Auto-generated method stub

    }

    private void refreshGallery(File file) {
        Intent mediaScanIntent = new Intent( Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
        mediaScanIntent.setData(Uri.fromFile(file));
        sendBroadcast(mediaScanIntent);
    }

    private class SaveImageTask extends AsyncTask<byte[], Void, Void> {

        @Override
        protected Void doInBackground(byte[]... data) {
            FileOutputStream outStream = null;

            // Write to SD Card
            try {
                File sdCard = Environment.getExternalStorageDirectory();
                File dir = new File (sdCard.getAbsolutePath() + "/camtest/");
                dir.mkdirs();
                String fileName = String.format("detect.jpg");
                File outFile = new File(dir, fileName);
                Log.v("file", outFile.toString());
                outStream = new FileOutputStream(outFile);
                outStream.write(data[0]);
                outStream.flush();
                outStream.close();

                Log.d("save", "onPictureTaken - wrote bytes: " + data.length + " to " + outFile.getAbsolutePath());

                refreshGallery(outFile);
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            } finally {
            }
            return null;
        }

    }

    public static void setCameraDisplayOrientation(Activity activity, int cameraId, android.hardware.Camera camera) {
        android.hardware.Camera.CameraInfo info = new android.hardware.Camera.CameraInfo();
        android.hardware.Camera.getCameraInfo(cameraId, info);
        int rotation = activity.getWindowManager().getDefaultDisplay().getRotation();
        int degrees = 0;
        switch (rotation) {
            case Surface.ROTATION_0:
                degrees = 0;
                break;
            case Surface.ROTATION_90:
                degrees = 90;
                break;
            case Surface.ROTATION_180:
                degrees = 180;
                break;
            case Surface.ROTATION_270:
                degrees = 270;
                break;
        }

        int result;
        if (info.facing == Camera.CameraInfo.CAMERA_FACING_FRONT) {
            result = (info.orientation + degrees) % 360;
            result = (360 - result) % 360; // compensate the mirror
        } else { // back-facing
            result = (info.orientation - degrees + 360) % 360;
        }
        camera.setDisplayOrientation(result);
    }

    public void detect_thumbnail(String imagecode){
        String data_test="{\"device_id\":\"1\",\"img\":\"data:image/jpeg;base64,"+imagecode.replace("\n", "")+"\"}";
        REQUEST request = new REQUEST();
        request.setdata(data_test);
        Log.v("api be", request.data);

        api.face_detection(request.data, new Callback<REQUEST>() {
            @Override
            public void success(REQUEST request, Response response) {
                Log.v("api", "success");
                //Log.v("api_all_al", String.valueOf(request.getfaces().length));
                if(request.getfaces()!=null){
                    if(request.getfaces().length!=0){
                        /*
                        Log.v("api_all", request.getfaces()[0].getname());
                        Log.v("api_all", String.valueOf(request.getfaces()[0].getprobability()));
                        Log.v("api_all", String.valueOf(request.getfaces()[0].getfid()));
                        Log.v("api_all", String.valueOf(request.getfaces()[0].getboundingbox()[0]));
                        Log.v("api_all", request.getfaces()[0].getthumnail().toString());
                        */
                        //byte[] decodedString =Base64.decode(request.getimg().split(",")[1], Base64.DEFAULT);
                        //thumbnail_decode = BitmapFactory.decodeByteArray(decodedString, 0, decodedString.length);
                        //Log.v("api af", request.toString());
                        String thumb = "http://175.126.82.175:20100/"+request.getfaces()[0].getthumnail();
                        HttpURLConnection connection = null;
                        try {
                            URL url = new URL(thumb);
                            connection = (HttpURLConnection) url.openConnection();
                            connection.setDoInput(true);
                            connection.connect();
                            InputStream input = connection.getInputStream();
                            thumbnail_decode = BitmapFactory.decodeStream(input);
                        } catch (IOException e) {
                            e.printStackTrace();
                            Log.v("result", e + "");
                        }finally{
                            if(connection!=null)connection.disconnect();
                        }
                        //String result = java.net.URLDecoder.decode("http://175.126.82.175:20100/"+request.getfaces()[0].getthumnail(), "UTF-8");
                        //thumbnail_decode = BitmapFactory.decodeByteArray(result.getBytes(), 0, result.length());

                        //scroll_layout
                        LinearLayout layout_parent = new LinearLayout(getApplicationContext());
                        if(request.getfaces()[0].getkind()==-0)
                            layout_parent.setBackgroundColor(Color.rgb(200,0,0));
                        else if(request.getfaces()[0].getkind()==1)
                            layout_parent.setBackgroundColor(Color.rgb(0,200,0));
                        else if(request.getfaces()[0].getkind()==2)
                            layout_parent.setBackgroundColor(Color.rgb(0,0,200));
                        else
                            layout_parent.setBackgroundColor(Color.rgb(0,0,0));
                        layout_parent.setOrientation(LinearLayout.VERTICAL);
                        layout_parent.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.FILL_PARENT));
                        LinearLayout.LayoutParams layout_parent1 = (LinearLayout.LayoutParams) layout_parent.getLayoutParams();
                        layout_parent1.leftMargin=10;
                        layout_parent1.rightMargin=10;
                        layout_parent.setLayoutParams(layout_parent1);

                        ImageView thumbnail_image = new ImageView(getApplicationContext());
                        thumbnail_image.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT));
                        if(thumbnail_image!=null) {
                            Log.v("thumbnail_image", "on");
                            thumbnail_image.setImageBitmap(thumbnail_decode);
                            imageview.setImageBitmap(thumbnail_decode);
                            imageview.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 2));
                            surfaceView.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 0));
                        } else {
                            Log.v("thumbnail_image", "off");
                            thumbnail_image.setImageBitmap(null);
                        }

                        TextView kind_text = new TextView(getApplicationContext());
                        kind_text.setLayoutParams(new LinearLayout.LayoutParams(ActionBar.LayoutParams.MATCH_PARENT, ActionBar.LayoutParams.WRAP_CONTENT));
                        kind_text.setText(String.valueOf(request.getfaces()[0].getname()));

                        TextView name_text = new TextView(getApplicationContext());
                        name_text.setLayoutParams(new LinearLayout.LayoutParams(ActionBar.LayoutParams.MATCH_PARENT, ActionBar.LayoutParams.WRAP_CONTENT));

                        name_text.setText((int)(request.getfaces()[0].getprobability() * 1000.1f)/10.0 + "%");

                        layout_parent.addView(kind_text);
                        layout_parent.addView(name_text);
                        layout_parent.addView(thumbnail_image);
                        scroll_layout.addView(layout_parent);
                    }
                    else {
                        LinearLayout layout_parent = new LinearLayout(getApplicationContext());
                        layout_parent.setBackgroundColor(Color.rgb(0,0,0));
                        layout_parent.setOrientation(LinearLayout.VERTICAL);
                        layout_parent.setLayoutParams(new LinearLayout.LayoutParams(ActionBar.LayoutParams.MATCH_PARENT, ActionBar.LayoutParams.FILL_PARENT));
                        LinearLayout.LayoutParams layout_parent1 = (LinearLayout.LayoutParams) layout_parent.getLayoutParams();
                        layout_parent1.leftMargin=10;
                        layout_parent1.rightMargin=10;
                        layout_parent.setLayoutParams(layout_parent1);

                        TextView not_find = new TextView(getApplicationContext());
                        not_find.setLayoutParams(new LinearLayout.LayoutParams(ActionBar.LayoutParams.MATCH_PARENT, ActionBar.LayoutParams.WRAP_CONTENT));
                        not_find.setText("Not Deteced");

                        layout_parent.addView(not_find);
                        scroll_layout.addView(layout_parent);
                    }
                }
            }

            @Override
            public void failure(RetrofitError error) {
                Toast.makeText(getApplicationContext(), "fail", Toast.LENGTH_SHORT);
                Log.v("api", "fail");
                Log.v("api", error.toString());
            }
        });
    }

    private static final int REQUEST_PHOTO_ALBOM = 1;
}
