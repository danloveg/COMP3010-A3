/**
 * DateInterface.java
 *
 * Author: Daniel Lovegrove
 */

import java.rmi.*;

public interface DateInterface extends Remote {
    public String echoDate() throws RemoteException;
}