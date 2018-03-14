/**
 * DaytimeClient2.java
 * 
 * Author: Daniel Lovegrove
 */

import java.io.*;
import java.rmi.*;
import java.util.IllegalFormatException;

public class DaytimeClient2 {
    public static void main(String[] args) {
        System.setProperty("java.security.policy", "./java.policy");

        try {
            if (args.length != 2) throw new IllegalArgumentException("Expects two arguments");
            String hostname = args[0];
            int port = Integer.parseInt(args[1]);
            String objectName = "CurrentDate";
            String url = "//" + hostname + ":" + port + "/" + objectName;

            DateInterface date = (DateInterface) Naming.lookup(url);
            System.out.print("Here is the timestamp received from the server: ");
            System.out.println(date.echoDate());

        } catch (NumberFormatException e) {
            System.out.println("Could not convert \"" + args[1] + "\" to an integer port number");
        } catch (IllegalArgumentException e) {
            System.out.println("Expected two arguments. Call like:");
            System.out.println("\tjava DaytimeClient2 <hostname> <port>");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
