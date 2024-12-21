/* Database Schema for debate web application.
   Note: MySQL supports a reduced form of full SQL, so this file should not be taken as
   an example of what to do in a full SQL database design.

   WARNING: RUNNING THIS DDL FILE WILL DELETE ANY EXISTING DEBATE TABLES IN THE DB!

   SqLite has no CHAR or VARCHAR types, only TEXT which can be any length.

   SqLite also has no DATETIME type so it is assume dates are stored as INTEGERs representing
   Julian time (the number of seconds passed since 1 Jan 1970). SqLite's date functions support
   storing dates this way.
 */

-- We have to explicitly enable foreign key support
PRAGMA foreign_keys = ON;

/* Users table. */
DROP TABLE IF EXISTS user;
CREATE TABLE user (
    userID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, -- Integer user ID / key
    userName TEXT NOT NULL,                            -- Login username
    passwordHash BLOB NOT NULL,                        -- Hashed password (bytes in python)
    isAdmin BOOLEAN NOT NULL,                          -- If user is admin or not. Ignore if not implementing admin
    creationTime INTEGER NOT NULL,                     -- Time user was created
    lastVisit INTEGER NOT NULL                         -- User's last visit, for showing new content when they return
);

/* Topic.
   Although updateTime could technically be calculated from the claim/reply tables, doing this for all
   topics whenever a user visited the site would be extremely slow. */
DROP TABLE IF EXISTS topic;
CREATE TABLE topic (
    topicID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,  -- Topic's ID number
    topicName TEXT NOT NULL,                             -- Topic's text
    postingUser INTEGER REFERENCES user(userID) ON DELETE SET NULL ON UPDATE CASCADE, -- FK (foreign key) of posting user
    creationTime INTEGER NOT NULL,                       -- Time topic was created
    updateTime INTEGER NOT NULL                          -- Last time a claim/reply was added
);

/* Claim, similar to topic. */
DROP TABLE IF EXISTS claim;
CREATE TABLE claim (
    claimID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,   -- CLaim ID number
    topic INTEGER NOT NULL REFERENCES topic(topicID) ON DELETE CASCADE ON UPDATE CASCADE, -- FK of claim
    postingUser INTEGER REFERENCES user(userID) ON DELETE SET NULL ON UPDATE CASCADE, -- FK of poisting user
    creationTime INTEGER NOT NULL,                       -- Time topic was created
    updateTime INTEGER NOT NULL,                         -- Last time a reply was added
    text TEXT NOT NULL                                   -- Actual text
);

/* For storing relationships between claims. First create a fixed table of the relation types,
   because SqLite doesn't support ENUMs.
 */
DROP TABLE IF EXISTS claimToClaimType;
CREATE TABLE claimToClaimType (
    claimRelTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    claimRelType TEXT NOT NULL
);
INSERT INTO claimToClaimType VALUES (1, "Opposed");
INSERT INTO claimToClaimType VALUES (2, "Equivalent");

/*
 Actual table for storing relationships between claims, since this is a many-to-many relationship.
 */
DROP TABLE IF EXISTS claimToClaim;
CREATE TABLE claimToClaim (
    claimRelID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,                        -- Claim relationship ID
    first INTEGER NOT NULL REFERENCES claim(claimID) ON DELETE CASCADE ON UPDATE CASCADE, -- FK of first related claim
    second INTEGER NOT NULL REFERENCES claim(claimID) ON DELETE CASCADE ON UPDATE CASCADE, -- FK of second related claim
    claimRelType INTEGER NOT NULL REFERENCES claimToClaimType(claimRelTypeID) ON DELETE CASCADE ON UPDATE CASCADE,
                                                                                            -- FK of type of relation
    /* Specify that there can't be several relationships between the same pair of two claims */
    CONSTRAINT claimToClaimUnique UNIQUE (first, second)
);

/* Replies can be made to either claims or other replies, so create a table to store the common parts of a
   reply (the text, poster, etc) separately from their relationship to other content.
 */
DROP TABLE IF EXISTS replyText;
CREATE TABLE replyText (
    replyTextID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,                           -- Reply ID
    postingUser INTEGER REFERENCES user(userID) ON DELETE SET NULL ON UPDATE CASCADE, -- FK of posting user
    creationTime INTEGER NOT NULL,                                                    -- Posting time
    text TEXT NOT NULL                                                                -- Text of reply
);

/* Store the relationships of claims to replies. */
DROP TABLE IF EXISTS replyToClaimType;
CREATE TABLE replyToClaimType (
    claimReplyTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    claimReplyType TEXT NOT NULL
);
INSERT INTO replyToClaimType VALUES (1, "Clarification");
INSERT INTO replyToClaimType VALUES (2, "Supporting Argument");
INSERT INTO replyToClaimType VALUES (3, "Counterargument");

DROP TABLE IF EXISTS replyToClaim;
CREATE TABLE replyToClaim (
    replyToClaimID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,                                       -- Relationship ID
    reply INTEGER NOT NULL REFERENCES replyText (replyTextID) ON DELETE CASCADE ON UPDATE CASCADE,   -- FK of related reply
    claim INTEGER NOT NULL REFERENCES claim (claimID) ON DELETE CASCADE ON UPDATE CASCADE,           -- FK of related claim
    replyToClaimRelType INTEGER NOT NULL REFERENCES replyToClaimType(claimReplyTypeID) ON DELETE CASCADE ON UPDATE CASCADE -- FK of relation type
);

/* Store the relationship of replies to other replies.
   Note that we use the replyText row as the FK for the "parent" reply (ie, the one this is a response to),
   because we do not know if it is a replyToClaim or another replyToReply.
   */
DROP TABLE IF EXISTS replyToReplyType;
CREATE TABLE replyToReplyType (
    replyReplyTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    replyReplyType TEXT NOT NULL
);
INSERT INTO replyToReplyType VALUES (1, "Evidence");
INSERT INTO replyToReplyType VALUES (2, "Support");
INSERT INTO replyToReplyType VALUES (3, "Rebuttal");


DROP TABLE IF EXISTS replyToReply;
CREATE TABLE replyToReply (
    replyToReplyID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,                                         -- Relationship ID
    reply INTEGER NOT NULL REFERENCES replyText(replyTextID) ON DELETE CASCADE ON UPDATE CASCADE,
    parent INTEGER NOT NULL REFERENCES replyText(replyTextID) ON DELETE CASCADE ON UPDATE CASCADE,
    replyToReplyRelType INTEGER NOT NULL REFERENCES replyToReplyType(replyReplyTypeID) ON DELETE CASCADE ON UPDATE CASCADE
)

