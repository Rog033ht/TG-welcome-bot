# Operator Quickstart

Fast daily-use guide for campaign operators.

## 1) Admin setup checklist

- You are included in `ADMIN_IDS` (Railway variable)
- Bot is added as admin in target channel (can post messages)
- Bot is online in Railway
- Railway service **Replicas = 1** (polling bots)

---

## 2) Core commands

- `/operator_help` - show operator commands
- `/asset_save NAME` - save replied photo/video as reusable asset
- `/campaign_create` - guided campaign builder
- `/campaign_cancel` - cancel current builder session
- `/template_save NAME` - save current button layout as template
- `/template_list` - list available templates
- `/template_apply NAME` - apply a template during campaign flow
- `/template_delete NAME` - delete an existing template

---

## 3) Save media asset (Step 2 dependency)

Step 2 of campaign asks for an **asset name**.  
That name comes from this command:

1. Send/forward a **photo or video** to bot chat
2. Reply to that media message:
   - `/asset_save promo1`
3. Bot confirms save

Now you can use `promo1` in campaign Step 2.

Important:
- Works with photo/video, not generic document files.

---

## 4) Build and publish a campaign

1. Send `/campaign_create`
2. Step 1: target channel/chat
   - `@your_channel` or `-1001234567890`
3. Step 2: asset name (e.g. `promo1`) or `skip`
4. Step 3: caption text (manual)
5. Step 4: buttons
   - Format: `Button Text | https://link.com`
   - `/row` = new row
   - `/done` = finish and preview
6. Step 5:
   - review preview
   - send `/publish` to post

Cancel anytime:
- `/campaign_cancel`

Template shortcut:
- after Step 2 (asset), send `/template_apply NAME`
- bot loads saved button layout (your caption stays unchanged)

---

## 5) Example session

1. Save asset:
   - Reply to media: `/asset_save welcome_vid`

2. Create campaign:
   - `/campaign_create`
   - `@my_channel`
   - `welcome_vid`
   - `🔥 New bonus live now. Claim habang available pa.`
   - `Claim Now | https://example.com/claim`
   - `Support | https://t.me/my_support`
   - `/done`
   - `/publish`

3. Save reusable template from active campaign:
   - `/template_save welcome_v1`

4. Next time (new asset only):
   - `/campaign_create`
   - `@my_channel`
   - `new_asset_today`
   - `/template_apply welcome_v1`
   - `/publish`

---

## 6) Common issues

- **New token rollout (recommended if bot feels “dead”)**
  1) Stop any local bot runs
  2) Ensure only ONE Railway service uses the token
  3) Update Railway `BOT_TOKEN` to the new token
  4) Redeploy
  5) Revoke the old token in BotFather

- **Asset not found**
  - You did not save it first with `/asset_save NAME`
  - Or name typo in Step 2

- **No response from bot**
  - Check Railway logs for startup errors
  - Confirm correct `BOT_TOKEN`
  - Confirm you are chatting with correct bot username

- **Template not found**
  - Check available names with `/template_list`
  - Template names are exact; avoid extra spaces

- **Conflict: other getUpdates request**
  - Same token running in another service/device
  - Keep only one active polling instance

---

## 7) Best practices

- Keep asset names clear: `daily_bonus_img`, `vip_video_1`
- Keep 1-2 CTA buttons per row for clean UI
- Use short, action-first button text (e.g. `Join Now`, `Claim Bonus`)
- Always preview before publish
