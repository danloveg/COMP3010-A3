/**
 * DaytimeClient2.java
 * 
 * Author: Daniel Lovegrove
 */

import java.io.*;
import java.rmi.*;
import java.util.IllegalFormatException;
import java.net.MalformedURLException;

public class DaytimeClient2 {
    public static void main(String[] args) {
        try {
            if (args.length != 2) throw new IllegalArgumentException("Expects two arguments");
            String hostname = args[0];
            int port = Integer.parseInt(args[1]);
            String currentDateUrl = "//" + hostname + ":" + port + "/CurrentDate";

            DateInterface date = (DateInterface) (Naming.lookup(currentDateUrl));
            System.out.print("Here is the timestamp received from the server: ");
            System.out.println(date.echoDate());

        } catch (NumberFormatException e) {
            System.out.println("Could not convert \"" + args[1] + "\" to an integer port number");
        } catch (IllegalArgumentException e) {
            System.out.println("Expected two arguments. Call like:");
            System.out.println("\tjava DaytimeClient2 <hostname> <port>");
        } catch (MalformedURLException e) {
            System.out.println(e.getMessage());
        } catch (RemoteException e) {
            System.out.println(e.getMessage());
        } catch (NotBoundException e) {
            System.out.println(e.getMessage());
        }
    }
}