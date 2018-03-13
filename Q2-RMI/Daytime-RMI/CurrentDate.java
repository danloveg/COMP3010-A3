/**
 * CurrentDate.java
 *
 * Author: Daniel Lovegrove
 */

import java.rmi.*;
import java.rmi.server.UnicastRemoteObject;

public class CurrentDate extends UnicastRemoteObject implements DateInterface {
    private String currentDate = "";

    public CurrentDate(String currentDate) throws RemoteException {
        this.currentDate = currentDate;
    }

    /**
     * Sends the currentDate instance variable.
     * @return The current date as a string
     */
    public String echoDate() throws RemoteException {
        return this.currentDate;
    }
}
