-- Simple PSX Users Setup
-- Run: psql -d your_database -f simple_users.sql

BEGIN;

INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('eef3633c-e001-4d06-a52b-dd0260bdb87f', 'user1', '{"name": "User 1", "password": "pass1", "project": "PSX"}', '2025-07-05T14:31:07.239170', '2025-07-05T14:31:07.239170');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('4d7ea06f-aca9-4705-902e-20379cc2e486', 'user2', '{"name": "User 2", "password": "pass2", "project": "PSX"}', '2025-07-05T14:31:07.239235', '2025-07-05T14:31:07.239235');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('f970d81e-11dd-49f5-9743-2127f36c58d3', 'user3', '{"name": "User 3", "password": "pass3", "project": "PSX"}', '2025-07-05T14:31:07.239270', '2025-07-05T14:31:07.239270');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('6c8bd1bf-4c84-49cc-b05e-41aada36226d', 'user4', '{"name": "User 4", "password": "pass4", "project": "PSX"}', '2025-07-05T14:31:07.239303', '2025-07-05T14:31:07.239303');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('c29b02ca-86ac-48f2-8be3-1e56073a35c5', 'user5', '{"name": "User 5", "password": "pass5", "project": "PSX"}', '2025-07-05T14:31:07.239328', '2025-07-05T14:31:07.239328');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('44006e27-73fe-43be-a9dd-4acfee99c0ef', 'user6', '{"name": "User 6", "password": "pass6", "project": "PSX"}', '2025-07-05T14:31:07.239349', '2025-07-05T14:31:07.239349');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('e34d8c24-8cdb-4abb-a169-a0f15f75c836', 'user7', '{"name": "User 7", "password": "pass7", "project": "PSX"}', '2025-07-05T14:31:07.239362', '2025-07-05T14:31:07.239362');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('43918c4b-cdb6-4395-8658-13a2c76e2cf0', 'user8', '{"name": "User 8", "password": "pass8", "project": "PSX"}', '2025-07-05T14:31:07.239377', '2025-07-05T14:31:07.239377');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('a0a82bc7-4b7f-44c6-8d06-dacf63aa9ceb', 'user9', '{"name": "User 9", "password": "pass9", "project": "PSX"}', '2025-07-05T14:31:07.239388', '2025-07-05T14:31:07.239388');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('61481ad4-0852-4a3f-b2fc-fe561168511a', 'user10', '{"name": "User 0", "password": "pass10", "project": "PSX"}', '2025-07-05T14:31:07.239431', '2025-07-05T14:31:07.239431');

COMMIT;
