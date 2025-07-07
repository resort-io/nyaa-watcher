CREATE TABLE `config` (
	`key` text PRIMARY KEY NOT NULL,
	`value` text
);
--> statement-breakpoint
CREATE TABLE `downloads` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`subscriptionID` integer NOT NULL,
	`success` integer NOT NULL,
	`title` text NOT NULL,
	`page` text NOT NULL,
	`hash` text NOT NULL,
	`datetime` text NOT NULL,
	FOREIGN KEY (`subscriptionID`) REFERENCES `webhooks`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE UNIQUE INDEX `downloads_subscriptionID_unique` ON `downloads` (`subscriptionID`);--> statement-breakpoint
CREATE TABLE `filter_exclude_regexes` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`filterID` integer NOT NULL,
	`value` text NOT NULL,
	FOREIGN KEY (`filterID`) REFERENCES `subscription_filters`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE UNIQUE INDEX `filter_exclude_regexes_filterID_unique` ON `filter_exclude_regexes` (`filterID`);--> statement-breakpoint
CREATE TABLE `filter_regexes` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`filterID` integer NOT NULL,
	`value` text NOT NULL,
	FOREIGN KEY (`filterID`) REFERENCES `subscription_filters`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE UNIQUE INDEX `filter_regexes_filterID_unique` ON `filter_regexes` (`filterID`);--> statement-breakpoint
CREATE TABLE `filter_tags` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`filterID` integer NOT NULL,
	`value` text NOT NULL,
	FOREIGN KEY (`filterID`) REFERENCES `subscription_filters`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE UNIQUE INDEX `filter_tags_filterID_unique` ON `filter_tags` (`filterID`);--> statement-breakpoint
CREATE TABLE `filter_webhooks` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`filterID` integer NOT NULL,
	`webhookID` integer NOT NULL,
	FOREIGN KEY (`filterID`) REFERENCES `subscription_filters`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`webhookID`) REFERENCES `webhooks`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE UNIQUE INDEX `filter_webhooks_filterID_unique` ON `filter_webhooks` (`filterID`);--> statement-breakpoint
CREATE UNIQUE INDEX `filter_webhooks_webhookID_unique` ON `filter_webhooks` (`webhookID`);--> statement-breakpoint
CREATE TABLE `subscription_filters` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`subscriptionID` integer NOT NULL,
	`name` text NOT NULL,
	FOREIGN KEY (`subscriptionID`) REFERENCES `webhooks`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE UNIQUE INDEX `subscription_filters_subscriptionID_unique` ON `subscription_filters` (`subscriptionID`);--> statement-breakpoint
CREATE UNIQUE INDEX `subscription_filters_name_unique` ON `subscription_filters` (`name`);--> statement-breakpoint
CREATE TABLE `subscription_webhooks` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`subscriptionID` integer NOT NULL,
	`webhookID` integer NOT NULL,
	FOREIGN KEY (`subscriptionID`) REFERENCES `webhooks`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`webhookID`) REFERENCES `webhooks`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE UNIQUE INDEX `subscription_webhooks_subscriptionID_unique` ON `subscription_webhooks` (`subscriptionID`);--> statement-breakpoint
CREATE UNIQUE INDEX `subscription_webhooks_webhookID_unique` ON `subscription_webhooks` (`webhookID`);--> statement-breakpoint
CREATE TABLE `webhooks` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`name` text NOT NULL,
	`type` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `webhooks_name_unique` ON `webhooks` (`name`);--> statement-breakpoint
CREATE TABLE `users` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`name` text NOT NULL,
	`type` text NOT NULL,
	`url` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `users_name_unique` ON `users` (`name`);--> statement-breakpoint
CREATE TABLE `webhook_config` (
	`webhookID` integer NOT NULL,
	`key` text PRIMARY KEY NOT NULL,
	`value` text,
	`description` text,
	FOREIGN KEY (`webhookID`) REFERENCES `webhooks`(`id`) ON UPDATE no action ON DELETE cascade
);
