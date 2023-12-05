import java.io.IOException;
import java.net.*;
import java.nio.ByteBuffer;
import java.util.Date;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class NTPClient {

    private static final String LOG_FILE = "other_log.csv";
    private static final String[] NTD_IP = {"172.16.26.3", "172.16.26.4", "172.16.26.7", "172.16.26.9", "172.17.26.10", "172.16.26.11", "172.16.26.12", "172.16.26.13", "172.16.26.14", "172.16.26.15", "172.17.26.16", "172.17.26.17"};
    private static final int SYNC_TIME = 60; // in seconds

    private static Socket tcpClient;
    private static ExecutorService threadPool;
    private static long timestamp;
    private static int openNtdCount;
    private static int bias;


    public static void main(String[] args) {
        start();
    }

    private static void start() {
        String ntpServerName = "time.nplindia.org"; // Replace with the desired NTP server
        bias = 0; // Replace with the desired bias

        System.out.print("Synchronizing NTD:-\n");
        for (String host : NTD_IP) {
            System.out.println(host + "\n");
        }

        try {
            loop(ntpServerName);
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("Alert: Unable to get NTP Time...");
            try {
                Thread.sleep(60000); // Sleep for 1 minute
            } catch (InterruptedException ex) {
                ex.printStackTrace();
            }
            System.out.println("RESTARTING...");
            start();
        }
    }

    private static void loop(String ntpServerName) throws Exception {
        while (true) {
            try {
                openNtdCount = 0;
                threadPool = Executors.newFixedThreadPool(NTD_IP.length);
                syncNtd(ntpServerName);
                while (openNtdCount > 0) {
                    Thread.sleep(1000);
                }
                threadPool.shutdown();
            } finally {
                if (tcpClient != null && !tcpClient.isClosed()) {
                    tcpClient.close();
                }
            }
            Thread.sleep(SYNC_TIME * 1000); // Sleep for SYNC_TIME seconds
        }
    }

    private static void syncNtd(String server) throws Exception {
        System.out.println("Please wait while getting time from " + server + "\r\n");
        NTPStats response = request(server);
        timestamp = Math.round(response.getTxTimestamp() + bias);
        System.out.println("NPLI NTP TIME: " + new Date(timestamp * 1000).toString() + "\r\n");

        for (String host : NTD_IP) {
            openNtdCount++;
            threadPool.execute(() -> {
                try {
                    sendTime(host, timestamp, server);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            });
        }
    }

    private static NTPStats request(String host) throws IOException {
        InetAddress address = InetAddress.getByName(host);
        DatagramSocket socket = new DatagramSocket();

        try {
            socket.setSoTimeout(5000); // Set socket timeout to 5 seconds

            NTPPacket queryPacket = new NTPPacket();
            queryPacket.setMode((byte) 3); // Mode 3 is client
            queryPacket.setVersion((byte) 3);


            DatagramPacket requestPacket = new DatagramPacket(queryPacket.toBytes(), queryPacket.toBytes().length, address, 123);
            socket.send(requestPacket);

            DatagramPacket responsePacket = new DatagramPacket(new byte[256], 256);
            socket.receive(responsePacket);

            NTPStats stats = new NTPStats();
            stats.fromBytes(responsePacket.getData());

            return stats;
        } finally {
            socket.close();
        }
    }

    private static void sendTime(String host, long timestamp, String server) throws IOException {
        String hostIp = host;
        int serverPort = 10000;
        tcpClient = new Socket(hostIp, serverPort);

        try {
            ByteBuffer buffer = ByteBuffer.allocate(28);
            buffer.put((byte) 0x55).put((byte) 0xAA).putInt(1).putInt(1).put((byte) 0xC1).putInt(15).putInt(15).put((byte) 0x10);
            buffer.putLong(timestamp * 1000); // Convert to milliseconds
            buffer.put((byte) 0).put((byte) 0).put((byte) 0x0D).put((byte) 0x0A);

            tcpClient.getOutputStream().write(buffer.array());

            byte[] received = new byte[1024];
            tcpClient.getInputStream().read(received);
            System.out.println(new Date(timestamp * 1000).toString() + ", " + host + ", Synchronized, " + bias + "\r\n");
        } catch (IOException e) {
            System.out.println(new Date(timestamp * 1000).toString() + ", " + host + ", Not Connected, " + bias + "\r\n");
        } finally {
            openNtdCount--;
            tcpClient.close();
        }
    }
}

class NTPStats extends NTPPacket {
    private long destTimestamp;

    // Constructors, getters, and setters omitted for brevity


    public void setDestTimestamp(long destTimestamp) {
        this.destTimestamp = destTimestamp;
    }
}