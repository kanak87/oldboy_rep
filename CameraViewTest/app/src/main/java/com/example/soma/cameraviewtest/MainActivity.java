package com.example.soma.cameraviewtest;

import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.PixelFormat;
import android.hardware.Camera;
import android.media.AudioManager;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.util.Base64;
import android.util.Log;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import com.example.soma.cameraviewtest.network.ApplicationController;
import com.example.soma.cameraviewtest.network.ServerInterface;
import com.example.soma.cameraviewtest.uuid.MyUUID;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;

import retrofit.Callback;
import retrofit.RetrofitError;
import retrofit.client.Response;

public class MainActivity extends AppCompatActivity implements SurfaceHolder.Callback{

    Camera camera;
    SurfaceView surfaceView;
    SurfaceHolder surfaceHolder;
    boolean previewing = false;;
    int count=0;
    String uuid="";
    private ServerInterface api;
    String imagecode;

    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        uuid = new MyUUID().getUUID(getApplicationContext());
        ApplicationController application = ApplicationController.getInstance();
        application.buildServerInterface("175.126.82.175", 20100);
        api = ApplicationController.getInstance().getServerInterface();

        Button buttonStartCameraPreview = (Button)findViewById(R.id.startcamerapreview);
        Button buttonStopCameraPreview = (Button)findViewById(R.id.stopcamerapreview);

        getWindow().setFormat(PixelFormat.UNKNOWN);
        surfaceView = (SurfaceView)findViewById(R.id.surfaceview);
        surfaceHolder = surfaceView.getHolder();
        surfaceHolder.addCallback(this);
        surfaceHolder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);

        buttonStartCameraPreview.setOnClickListener(new Button.OnClickListener(){

            @Override
            public void onClick(View v) {
                // TODO Auto-generated method stub
                if(!previewing){
                    camera = Camera.open(Camera.CameraInfo.CAMERA_FACING_FRONT);
                    if (camera != null){
                        try {
                            camera.setPreviewDisplay(surfaceHolder);
                            camera.setDisplayOrientation(90);
                            Camera.Parameters params = null;
                            camera.startPreview();
                            camera.setFaceDetectionListener(new MyFaceDetectionListener());
                            camera.startFaceDetection();

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
            }});

    }

    class MyFaceDetectionListener implements Camera.FaceDetectionListener {

        @Override
        public void onFaceDetection(Camera.Face[] faces, Camera camera) {
            if (faces.length > 0){
                Log.v("detect", count + "");
                count++;
                if(count%100==0) {
                    //take picture
                    camera.takePicture(shutterCallback, rawCallback, jpegCallback);
                    //img change

                }
            }
        }
    }

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
            Bitmap bm = BitmapFactory.decodeFile("/storage/emulated/0/camtest/detect.jpg");
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            bm.compress(Bitmap.CompressFormat.JPEG, 100, bos); //저장된이미지를 jpeg로 포맷 품질100으로하여 출력
            byte[] ba = bos.toByteArray();
            imagecode= Base64.encodeToString(ba, Base64.DEFAULT);
            Log.v("base64", String.valueOf(imagecode.length()));
            String data_test="{\"device_id\":\"1\",\"img\":\"data:image/jpeg;base64,"+imagecode.replace("\n", "")+"\"}";
            Log.v("api test", String.valueOf(data_test.length()));
            Log.v("api test", data_test);
            REQUEST request = new REQUEST();
            request.setdata(data_test);
            //Log.v("api be", request.data);
            api.face_detection(request.data, new Callback<REQUEST>() {
                @Override
                public void success(REQUEST request, Response response) {
                    Log.v("api", "success");
                    //Log.v("api af", request.toString());
                    Log.v("api", request.getResult());

                }

                @Override
                public void failure(RetrofitError error) {
                    Toast.makeText(getApplicationContext(), "fail", Toast.LENGTH_SHORT);
                    Log.v("api", "fail");
                    Log.v("api", error.toString());
                }
            });
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
}
