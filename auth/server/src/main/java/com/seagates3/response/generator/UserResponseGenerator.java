/*
 * COPYRIGHT 2015 SEAGATE LLC
 *
 * THIS DRAWING/DOCUMENT, ITS SPECIFICATIONS, AND THE DATA CONTAINED
 * HEREIN, ARE THE EXCLUSIVE PROPERTY OF SEAGATE TECHNOLOGY
 * LIMITED, ISSUED IN STRICT CONFIDENCE AND SHALL NOT, WITHOUT
 * THE PRIOR WRITTEN PERMISSION OF SEAGATE TECHNOLOGY LIMITED,
 * BE REPRODUCED, COPIED, OR DISCLOSED TO A THIRD PARTY, OR
 * USED FOR ANY PURPOSE WHATSOEVER, OR STORED IN A RETRIEVAL SYSTEM
 * EXCEPT AS ALLOWED BY THE TERMS OF SEAGATE LICENSES AND AGREEMENTS.
 *
 * YOU SHOULD HAVE RECEIVED A COPY OF SEAGATE'S LICENSE ALONG WITH
 * THIS RELEASE. IF NOT PLEASE CONTACT A SEAGATE REPRESENTATIVE
 * http://www.seagate.com/contact
 *
 * Original author:  Arjun Hariharan <arjun.hariharan@seagate.com>
 * Original creation date: 13-Dec-2015
 */
package com.seagates3.response.generator;

import com.seagates3.model.User;
import com.seagates3.response.ServerResponse;
import com.seagates3.response.formatter.xml.XMLResponseFormatter;
import java.util.ArrayList;
import java.util.LinkedHashMap;

public class UserResponseGenerator extends AbstractResponseGenerator {

    public ServerResponse generateCreateResponse(User user) {
        LinkedHashMap responseElements = new LinkedHashMap();
        responseElements.put("Path", user.getPath());
        responseElements.put("UserName", user.getName());
        responseElements.put("UserId", user.getId());

        String arnValue = String.format("arn:aws:iam::1:user/%s", user.getName());
        responseElements.put("Arn", arnValue);

        return new XMLResponseFormatter().formatCreateResponse("CreateUser",
                "User", responseElements, "0000");
    }

    public ServerResponse generateDeleteResponse() {
        return new XMLResponseFormatter().formatDeleteResponse("DeleteUser");
    }

    public ServerResponse generateListResponse(Object[] responseObjects) {
        User[] userList = (User[]) responseObjects;

        ArrayList<LinkedHashMap<String, String>> userMemebers = new ArrayList<>();
        LinkedHashMap responseElements;

        for (User user : userList) {
            responseElements = new LinkedHashMap();
            responseElements.put("UserId", user.getId());
            responseElements.put("Path", user.getPath());
            responseElements.put("UserName", user.getName());

            String arn = "arn:aws:iam::000:user/" + user.getName();
            responseElements.put("Arn", arn);
            responseElements.put("createDate", user.getCreateDate());

            /**
             * TODO - Replace password last used
             */
            responseElements.put("PasswordLastUsed", "");

            userMemebers.add(responseElements);
        }

        return new XMLResponseFormatter().formatListResponse("ListUsers",
                "Users", userMemebers, false, "0000");
    }

    public ServerResponse generateUpdateResponse() {
        return new XMLResponseFormatter().formatUpdateResponse("UpdateUser");
    }
}