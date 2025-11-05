INSERT INTO conversation (id, title, current_prd_version_id, status, metadata, created_at, updated_at) VALUES
(1, 'E-commerce App for Artisans', 2, 'active', '{"user_id": "user_sarah_101", "persona": "Startup Founder"}', '2025-11-10 09:15:00', '2025-11-11 14:30:00'),
(2, 'SaaS Project Management Tool', 3, 'active', '{"user_id": "user_mike_202", "persona": "Product Manager"}', '2025-11-12 11:00:00', '2025-11-12 16:45:00'),
(3, 'Healthcare Patient Portal', NULL, 'active', '{"user_id": "user_david_404", "persona": "Consultant"}', '2025-11-13 10:05:00', '2025-11-13 10:07:00'),
(4, 'Personal Finance Budgeting App', 4, 'archived', '{"user_id": "user_jessica_303", "persona": "Development Team Lead"}', '2025-11-08 14:20:00', '2025-11-08 17:00:00');

INSERT INTO message (id, conversation_id, sender, message_type, content, metadata, status, created_at, updated_at) VALUES
(1, 1, 'user', 'text', 'I want to build a mobile app for local artisans to sell their handmade goods online. It should be like Etsy but focused on our local community. Users should be able to browse products, add them to a cart, and check out using a credit card. Sellers need a dashboard to manage their products and orders.', '{"client_ip": "78.12.34.56"}', 'delivered', '2025-11-10 09:15:02', '2025-11-10 09:15:02'),
(2, 1, 'user', 'file', 'Uploaded file: initial_notes.txt', '{"file_attachment_id": 1}', 'delivered', '2025-11-10 09:16:10', '2025-11-10 09:16:10'),
(3, 1, 'ai', 'system', 'Analyzing your problem statement and attached file. This may take a few moments.', '{"processing_time_ms": 150}', 'delivered', '2025-11-10 09:16:12', '2025-11-10 09:16:12'),
(4, 1, 'ai', 'text', 'Analysis complete. I have identified the core features and potential user personas. To refine the requirements, I have a few clarifying questions for you. Please answer them to help me generate a more accurate PRD.', '{"analysis_id": "analysis_abc123"}', 'delivered', '2025-11-10 09:18:30', '2025-11-10 09:18:30'),
(5, 1, 'user', 'text', 'We should support both Stripe and PayPal for payments.', '{"is_clarification_response": true, "question_id": 1}', 'delivered', '2025-11-10 10:05:15', '2025-11-10 10:05:15'),
(6, 1, 'user', 'text', 'Yes, a 5% commission on each sale sounds right for the platform fee.', '{"is_clarification_response": true, "question_id": 2}', 'delivered', '2025-11-10 10:06:00', '2025-11-10 10:06:00'),
(7, 1, 'ai', 'system', 'Thank you. Generating the first version of your Product Requirements Document based on your answers.', '{"trigger": "clarification_answered"}', 'delivered', '2025-11-10 10:06:05', '2025-11-10 10:06:05'),
(8, 1, 'ai', 'text', 'I have generated the first version of the PRD. You can review it now. Let me know if you''d like any changes.', '{"prd_version_id": 1}', 'delivered', '2025-11-10 10:08:00', '2025-11-10 10:08:00'),
(9, 1, 'user', 'text', 'This looks great! Can you please add a user story for a customer review and rating system?', NULL, 'delivered', '2025-11-11 14:28:00', '2025-11-11 14:28:00'),
(10, 1, 'ai', 'text', 'Of course. I have updated the PRD to include a new section for ''Customer Feedback'' with user stories for reviews and ratings. This is now version 2.', '{"prd_version_id": 2, "change_summary": "Added customer review and rating system."}', 'delivered', '2025-11-11 14:30:00', '2025-11-11 14:30:00'),
(11, 2, 'user', 'text', 'We need a new SaaS tool for agile project management. Key features should include Kanban boards, task assignments, due dates, comments on tasks, and basic reporting on project progress. It needs to be super intuitive for non-technical teams. We should also have different user roles like Admin, Member, and Viewer.', NULL, 'delivered', '2025-11-12 11:00:30', '2025-11-12 11:00:30'),
(12, 2, 'ai', 'system', 'Processing your request to generate a PRD for an agile project management tool.', NULL, 'delivered', '2025-11-12 11:00:32', '2025-11-12 11:00:32'),
(13, 2, 'ai', 'text', 'Based on your input, I have generated an initial PRD draft. I have also identified some areas that need more detail. Please review the following questions when you have a moment.', '{"analysis_id": "analysis_def456"}', 'delivered', '2025-11-12 11:03:00', '2025-11-12 11:03:00'),
(14, 2, 'user', 'text', 'For reporting, let''s start with a simple burndown chart and a task completion report by user.', '{"is_clarification_response": true, "question_id": 3}', 'delivered', '2025-11-12 16:45:00', '2025-11-12 16:45:00'),
(15, 3, 'user', 'text', 'A secure web portal for patients to view their medical records, schedule appointments with their doctors, and request prescription refills.', NULL, 'delivered', '2025-11-13 10:05:10', '2025-11-13 10:05:10'),
(16, 3, 'ai', 'system', 'Thank you for the problem statement. I am beginning the analysis to identify key requirements, personas, and potential compliance considerations like HIPAA. I will ask clarifying questions shortly.', '{"initial_analysis": "started"}', 'delivered', '2025-11-13 10:07:00', '2025-11-13 10:07:00'),
(17, 4, 'user', 'text', 'I need a simple mobile app for iOS and Android that helps users track their daily expenses and set monthly budgets for different categories like food, transport, and entertainment. It should have a clean UI and provide simple charts to visualize spending.', NULL, 'delivered', '2025-11-08 14:20:15', '2025-11-08 14:20:15'),
(18, 4, 'ai', 'text', 'Understood. I have generated a complete PRD for a personal finance budgeting app based on your description. It includes user stories for expense tracking, budget creation, and data visualization. Please review it.', '{"prd_version_id": 4}', 'delivered', '2025-11-08 14:25:00', '2025-11-08 14:25:00');

INSERT INTO file_attachment (id, conversation_id, original_filename, file_type, file_size, storage_path, extracted_text, status, metadata, created_at, updated_at) VALUES
(1, 1, 'initial_notes.txt', 'txt', 1234, 's3://prd-analyzer-bucket/user_sarah_101/conv_1/initial_notes.txt', 'User types: Buyers (local residents) and Sellers (artisans). Sellers need a simple way to upload photos and descriptions of their items. We need a secure checkout process. Maybe we can feature a different artisan on the homepage each week. The app should be available on both iOS and Android.', 'processed', '{"text_extraction_engine": "tika_v2.1"}', '2025-11-10 09:16:08', '2025-11-10 09:17:15');

INSERT INTO prd_version (id, conversation_id, version_number, content, change_summary, generated_by_ai_message_id, trigger_type, status, metadata, created_at, updated_at) VALUES
(1, 1, 1, '# PRD: Artisan Marketplace App (v1.0)

## 1. Executive Summary
This document outlines the requirements for "Artisan Local", a mobile application designed to connect local artisans with customers in their community, providing a platform for selling handmade goods.

## 2. User Personas
- **The Artisan (Seller):** Maria, 45, a jewelry maker. Needs an easy way to list products and manage sales without technical expertise.
- **The Buyer (Customer):** Alex, 32, a supporter of local businesses. Wants to discover unique, locally-made products.

## 3. User Stories
- As a Buyer, I want to browse products by category, so I can find what I''m looking for.
- As a Seller, I want to create a product listing with photos and a description, so I can showcase my work.
- As a Buyer, I want to pay with my credit card or PayPal, so I can complete my purchase securely.

## 4. Non-Functional Requirements
- **Payment:** Integration with Stripe and PayPal.
- **Platform Fee:** A 5% commission will be charged on all sales.
- **Security:** All user data must be encrypted in transit and at rest.', 'Initial PRD generated from user input and clarifications.', 8, 'clarification', 'complete', '{"word_count": 250}', '2025-11-10 10:08:00', '2025-11-10 10:08:00'),
(2, 1, 2, '# PRD: Artisan Marketplace App (v2.0)

## 1. Executive Summary
This document outlines the requirements for "Artisan Local", a mobile application designed to connect local artisans with customers in their community, providing a platform for selling handmade goods.

## 2. User Personas
- **The Artisan (Seller):** Maria, 45, a jewelry maker. Needs an easy way to list products and manage sales without technical expertise.
- **The Buyer (Customer):** Alex, 32, a supporter of local businesses. Wants to discover unique, locally-made products.

## 3. User Stories
- As a Buyer, I want to browse products by category, so I can find what I''m looking for.
- As a Seller, I want to create a product listing with photos and a description, so I can showcase my work.
- As a Buyer, I want to pay with my credit card or PayPal, so I can complete my purchase securely.
- **As a Buyer, I want to leave a rating and a written review for a product I purchased, so that I can share my feedback with other potential buyers.**

## 4. Non-Functional Requirements
- **Payment:** Integration with Stripe and PayPal.
- **Platform Fee:** A 5% commission will be charged on all sales.
- **Security:** All user data must be encrypted in transit and at rest.', 'Added user story for customer review and rating system.', 10, 'edit', 'complete', '{"word_count": 285}', '2025-11-11 14:30:00', '2025-11-11 14:30:00'),
(3, 2, 1, '# PRD: AgileFlow PM Tool (v1.0)

## 1. Executive Summary
AgileFlow is a SaaS project management tool designed for non-technical teams to manage projects using agile methodologies. It prioritizes simplicity and visual management.

## 2. User Roles
- **Admin:** Can manage billing, users, and all project settings.
- **Member:** Can create and manage tasks within a project.
- **Viewer:** Has read-only access to projects.

## 3. User Stories
- As a Member, I want to view tasks on a Kanban board, so I can visualize the workflow.
- As an Admin, I want to invite new users to the workspace, so my team can collaborate.

## 4. Reporting
- Burndown Chart
- Task Completion Report by User

## 5. Open Questions
- What third-party integrations are required (e.g., Slack, GitHub)?
- What are the specific requirements for task notifications?', 'Initial PRD generated from user input.', 13, 'initial', 'complete', '{"word_count": 180}', '2025-11-12 11:03:00', '2025-11-12 11:03:00'),
(4, 4, 1, '# PRD: Budget Buddy App (v1.0)

## 1. Executive Summary
Budget Buddy is a cross-platform mobile application that helps users track expenses and manage monthly budgets to improve their financial health.

## 2. User Personas
- **The Young Professional:** Sam, 28, wants to save for a down payment and needs to control spending.

## 3. User Stories
- As a user, I want to quickly add a new expense with a category and amount, so I can log my spending on the go.
- As a user, I want to set a monthly budget for a category, so I can be alerted when I am close to my limit.
- As a user, I want to see a pie chart of my spending by category, so I can understand where my money is going.

## 4. Technical Requirements
- **Platform:** iOS and Android.
- **UI Framework:** React Native is recommended for cross-platform development.', 'Initial PRD from a concise problem statement.', 18, 'initial', 'complete', '{"word_count": 210}', '2025-11-08 14:25:00', '2025-11-08 14:25:00');

INSERT INTO clarifying_question (id, conversation_id, prd_version_id, question_text, category, priority, ai_message_id, user_message_id, answer, status, metadata, created_at, updated_at) VALUES
(1, 1, 1, 'What payment gateways do you plan to support for checkout?', 'functional', 1, 4, 5, 'We should support both Stripe and PayPal for payments.', 'answered', NULL, '2025-11-10 09:18:30', '2025-11-10 10:05:15'),
(2, 1, 1, 'Will the platform charge a commission fee on sales made by artisans? If so, what is the proposed percentage?', 'business', 0, 4, 6, 'Yes, a 5% commission on each sale sounds right for the platform fee.', 'answered', NULL, '2025-11-10 09:18:30', '2025-11-10 10:06:00'),
(3, 2, 3, 'You mentioned "basic reporting". Could you specify which reports are essential for the first version?', 'functional', 1, 13, 14, 'For reporting, let''s start with a simple burndown chart and a task completion report by user.', 'answered', NULL, '2025-11-12 11:03:00', '2025-11-12 16:45:00'),
(4, 2, 3, 'Should there be a notification system for events like task assignment, comments, or approaching due dates?', 'functional', 0, 13, NULL, NULL, 'unanswered', NULL, '2025-11-12 11:03:00', '2025-11-12 11:03:00'),
(5, 2, 3, 'Are there any plans for third-party integrations, such as with Slack, Google Drive, or GitHub?', 'technical', 0, 13, NULL, NULL, 'unanswered', NULL, '2025-11-12 11:03:00', '2025-11-12 11:03:00');

INSERT INTO prd_change (id, prd_version_id, previous_prd_version_id, section, change_type, old_content, new_content, reason, metadata, created_at) VALUES
(1, 2, 1, 'user_stories', 'added', NULL, '- As a Buyer, I want to leave a rating and a written review for a product I purchased, so that I can share my feedback with other potential buyers.', 'User requested a customer review and rating system via chat.', '{"source": "chat_message_id_9"}', '2025-11-11 14:30:00');

INSERT INTO export (id, prd_version_id, conversation_id, export_format, file_path, status, metadata, created_at, updated_at) VALUES
(1, 2, 1, 'pdf', 's3://prd-analyzer-exports/user_sarah_101/Artisan_Marketplace_App_v2.0.pdf', 'completed', '{"page_count": 5}', '2025-11-11 15:00:00', '2025-11-11 15:00:05'),
(2, 2, 1, 'json', 's3://prd-analyzer-exports/user_sarah_101/Artisan_Marketplace_App_v2.0_stories.json', 'completed', '{"user_stories_exported": 4}', '2025-11-11 15:01:00', '2025-11-11 15:01:02'),
(3, 4, 4, 'markdown', 's3://prd-analyzer-exports/user_jessica_303/Budget_Buddy_App_v1.0.md', 'completed', '{"word_count": 210}', '2025-11-08 16:55:00', '2025-11-08 16:55:01');