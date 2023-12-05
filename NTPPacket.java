import java.nio.ByteBuffer;

public class NTPPacket {
    private byte leap;
    private byte version;
    private byte mode;
    private byte stratum;
    private byte poll;
    private byte precision;
    private int rootDelay;
    private int rootDispersion;
    private int refId;
    private long refTimestamp;
    private long origTimestamp;
    private long recvTimestamp;
    private long txTimestamp;

    // Constructors, getters, and setters omitted for brevity

    public void setMode(byte mode) {
        this.mode = mode;
    }

    public void setVersion(byte version) {
        this.version = version;
    }

    public byte[] toBytes() {
        ByteBuffer buffer = ByteBuffer.allocate(48);
        buffer.put((byte) ((leap << 6) | (version << 3) | mode));
        buffer.put(stratum);
        buffer.put(poll);
        buffer.put(precision);
        buffer.putInt(rootDelay);
        buffer.putInt(rootDispersion);
        buffer.putInt(refId);
        buffer.putLong(refTimestamp);
        buffer.putLong(origTimestamp);
        buffer.putLong(recvTimestamp);
        buffer.putLong(txTimestamp);
        return buffer.array();
    }


    public void fromBytes(byte[] data) {
        ByteBuffer buffer = ByteBuffer.wrap(data);
        leap = buffer.get();
        version = buffer.get();
        mode = buffer.get();
        stratum = buffer.get();
        poll = buffer.get();
        precision = buffer.get();
        rootDelay = buffer.getInt();
        rootDispersion = buffer.getInt();
        refId = buffer.getInt();
        refTimestamp = buffer.getLong();
        origTimestamp = buffer.getLong();
        recvTimestamp = buffer.getLong();
        txTimestamp = buffer.getLong();
    }


    public long getTxTimestamp() {
        return txTimestamp;
    }
}
