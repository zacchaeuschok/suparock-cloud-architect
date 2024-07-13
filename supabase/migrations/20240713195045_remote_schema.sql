revoke delete on table "public"."web_service_documents" from "anon";

revoke insert on table "public"."web_service_documents" from "anon";

revoke references on table "public"."web_service_documents" from "anon";

revoke select on table "public"."web_service_documents" from "anon";

revoke trigger on table "public"."web_service_documents" from "anon";

revoke truncate on table "public"."web_service_documents" from "anon";

revoke update on table "public"."web_service_documents" from "anon";

revoke delete on table "public"."web_service_documents" from "authenticated";

revoke insert on table "public"."web_service_documents" from "authenticated";

revoke references on table "public"."web_service_documents" from "authenticated";

revoke select on table "public"."web_service_documents" from "authenticated";

revoke trigger on table "public"."web_service_documents" from "authenticated";

revoke truncate on table "public"."web_service_documents" from "authenticated";

revoke update on table "public"."web_service_documents" from "authenticated";

revoke delete on table "public"."web_service_documents" from "service_role";

revoke insert on table "public"."web_service_documents" from "service_role";

revoke references on table "public"."web_service_documents" from "service_role";

revoke select on table "public"."web_service_documents" from "service_role";

revoke trigger on table "public"."web_service_documents" from "service_role";

revoke truncate on table "public"."web_service_documents" from "service_role";

revoke update on table "public"."web_service_documents" from "service_role";

drop function if exists "public"."match_web_service_documents"(query_embedding vector, filter jsonb);

alter table "public"."web_service_documents" drop constraint "web_service_documents_pkey";

drop index if exists "public"."web_service_documents_pkey";

drop table "public"."web_service_documents";


