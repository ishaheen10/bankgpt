-- PSX Chainlit Users Setup Script
-- Run this script against your PostgreSQL database

BEGIN;

INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('8e763774-306e-4809-ba2d-1c6e528cb0a0', 'analyst1', '{"role": "analyst", "name": "Financial Analyst 1", "project": "PSX", "password_hash": "4162a8a3e3ab7ba4752480b4e0abadcbb41677deef9cd6c0afa044b2f0e79217", "salt": "ec1a707db0b7ffb3d78fa374665bff1378f48bb213ad3429deb4a2bf013c4a93", "created_by": "setup_script", "permissions": {"read": true, "analyze": true, "export": true}}', '2025-07-05T14:21:33.193387', '2025-07-05T14:21:33.193387');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('4e788603-c65c-4f6c-a566-4cbbf6228a39', 'analyst2', '{"role": "analyst", "name": "Financial Analyst 2", "project": "PSX", "password_hash": "96b5868e15f673b944a096a755a3f7324f531a060e568867a04a192a52fc73b5", "salt": "6146cc24a9f0001ef74140ddb885e2d065e020b014180320982102979b06f702", "created_by": "setup_script", "permissions": {"read": true, "analyze": true, "export": true}}', '2025-07-05T14:21:33.219594', '2025-07-05T14:21:33.219594');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('a6b82739-28f6-4aeb-a9d9-d6e98841baa2', 'manager1', '{"role": "manager", "name": "Portfolio Manager 1", "project": "PSX", "password_hash": "f91f4838c5a19f499915bcff2e580c7afd6a1fefc0945ff74629b550731ca957", "salt": "bc976b4aaa1cf887e2e04b7ed6facc72ef7d177559c4f05a978b80b8eb9942d7", "created_by": "setup_script", "permissions": {"read": true, "analyze": true, "export": true}}', '2025-07-05T14:21:33.247024', '2025-07-05T14:21:33.247024');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('62517a26-6e96-4a5e-81a4-92ffd89201ff', 'manager2', '{"role": "manager", "name": "Portfolio Manager 2", "project": "PSX", "password_hash": "db056874ac0980d2e9d1fd3d9fc896d905dabadff0333443347b759eeae36be7", "salt": "dd14ff426916f58c96341a7355f1c252c1bc77b3fd63807445338273d7cb595c", "created_by": "setup_script", "permissions": {"read": true, "analyze": true, "export": true}}', '2025-07-05T14:21:33.272949', '2025-07-05T14:21:33.272949');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('0028de64-16f6-442a-b42d-a0ded2b999c0', 'researcher1', '{"role": "researcher", "name": "Research Associate 1", "project": "PSX", "password_hash": "34dbceaadcd9dc7afb9919c63bc975804787442c73c3891a433031454e762407", "salt": "7526aee33b1f0146ede8e626ceb04696ef2f36a54fe48f8166a4785c7c7556c4", "created_by": "setup_script", "permissions": {"read": true, "analyze": true, "export": false}}', '2025-07-05T14:21:33.299999', '2025-07-05T14:21:33.299999');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('4a896341-0fe0-4f8b-9fb4-c4b841525539', 'researcher2', '{"role": "researcher", "name": "Research Associate 2", "project": "PSX", "password_hash": "eb6f86b3ef9f8e21f755005c04027083e0408e657e894394a6cd1b56ba59a24f", "salt": "30c684b5ccd5ac28e4c9bf916f7c07ffcf3d52d0244e08b5fade1ebffc1981da", "created_by": "setup_script", "permissions": {"read": true, "analyze": true, "export": false}}', '2025-07-05T14:21:33.325628', '2025-07-05T14:21:33.325628');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('bbe9f6dc-81a5-4065-8bed-f5a4293f5bfa', 'trader1', '{"role": "trader", "name": "Trading Specialist 1", "project": "PSX", "password_hash": "24d839ffc8322416738455a449d4475a923d3a4ec7abf00277d5600ecf8fc555", "salt": "b6f936368b2e18f9b85aeb535822e87f2f2d71159379012a03322fbf8631d69c", "created_by": "setup_script", "permissions": {"read": true, "analyze": true, "export": false}}', '2025-07-05T14:21:33.352762', '2025-07-05T14:21:33.352762');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('b987b72c-2e30-40a4-8d20-130080518e48', 'trader2', '{"role": "trader", "name": "Trading Specialist 2", "project": "PSX", "password_hash": "f8d6cdc086c63aef1876c0621ea0917dd5bb3bba75fa681b9ac6ee70fee2b432", "salt": "8fa32385f21856b3b7b534a8a8faefacc813499b257bd53e44b711284e4f7271", "created_by": "setup_script", "permissions": {"read": true, "analyze": true, "export": false}}', '2025-07-05T14:21:33.378525', '2025-07-05T14:21:33.378525');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('d6eb8b38-ae5e-450a-bd5d-92332793063a', 'risk_analyst', '{"role": "risk_analyst", "name": "Risk Analyst", "project": "PSX", "password_hash": "c27123199942e3368873e1267abd5627ba6355bed92f9e0bcde960d8bad320cd", "salt": "2697fbd548b1a2f6fa21b0b6bdfe99bc3bb912e7b478c8db30294f68f50036fb", "created_by": "setup_script", "permissions": {"read": true, "analyze": true, "export": true}}', '2025-07-05T14:21:33.405725', '2025-07-05T14:21:33.405725');
INSERT INTO "User" (id, identifier, metadata, "createdAt", "updatedAt") 
VALUES ('b8101a12-deb7-4975-a74e-13273e359367', 'compliance', '{"role": "compliance", "name": "Compliance Officer", "project": "PSX", "password_hash": "a475fa7691b3040898008becc69fa293fb5dfd3f1cc43d0275433d385d54c8fa", "salt": "750d80ce5d0af1becde2cdc738b279c4f2231d6cae9762b3aebcfd4a5264849e", "created_by": "setup_script", "permissions": {"read": true, "analyze": true, "export": false}}', '2025-07-05T14:21:33.431859', '2025-07-05T14:21:33.431859');

COMMIT;
