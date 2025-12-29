import os
import asyncio
from typing import List, Dict

import discord
from discord import app_commands
from discord.ext import commands
from pymongo import MongoClient

# ------------- INTENTS (correct + unified) -------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# ------------- CONFIG -------------

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # set in Railway
MONGODB_URI = os.getenv("MONGODB_URI")      # set in Railway
DB_NAME = "blueprint_market"
COLLECTION_NAME = "blueprints"

# ------------- STATIC BLUEPRINT CATALOG -------------

# Filled from the list you provided, alphabetized by name.
# Name -> Thumbnail URL
BLUEPRINT_CATALOG: Dict[str, str] = {
    "Angled Grip II": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236182307770378/Angled_Grip_II_Blueprint.webp?ex=6953fdce&is=6952ac4e&hm=4b7b217319059cf0c4a6dd094db00f87cfa9341d444ee4e37c369767c6f7efe8&",
    "Angled Grip III": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236182613950494/Angled_Grip_III_Blueprint.webp?ex=6953fdce&is=6952ac4e&hm=db5d9a04d834bb63dc85413146045038a8476d1cd9ef84965c7bb987bfaccbcd&",
    "Anvil": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236182924591135/Anvil_Blueprint.webp?ex=6953fdce&is=6952ac4e&hm=151400f73c13ecb47a4a4de78e700cbb3814c90c698d1580b0d0b6ff0bd1e272&",
    "Aphelion": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236183247294464/Aphelion_Blueprint.webp?ex=6953fdcf&is=6952ac4f&hm=07119076827c89d4169c50bdd8e436e1df8a9a3f15202880592cdfa761cd7f11&",
    "Barricade Kit": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236183545086083/Barrcade_Kit_Blueprint.webp?ex=6953fdcf&is=6952ac4f&hm=9c233045caa33bed6f2fbbdbd044bbd21f6071443be9c2ff9bccbc7daa3d91aa&",
    "Bettina": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236183847337984/Bettina_Blueprint.webp?ex=6953fdcf&is=6952ac4f&hm=37ffae88ce75e573cdcaf17c2aedb964fc6eb45ae47006601da130336f104afb&",
    "Blaze Grenade": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236184144875787/Blaze_Grenade_Blueprint.webp?ex=6953fdcf&is=6952ac4f&hm=36110d352419fd4e777dc0a4b0e1f5ea21a74496f4ed4e7b1e165b7b79480489&",
    "Blue Light Stick": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236184476221522/Blue_Light_Stick_Blueprint.webp?ex=6953fdcf&is=6952ac4f&hm=9a677d69681a83b616ed943d41c4f3f7ec76e72051b60cdb4a8c568b486fcd12&",
    "Bobcat": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236184786735104/Bobcat_Blueprint.webp?ex=6953fdcf&is=6952ac4f&hm=b7c6055327c601b69096524419a815ec6be0d46f39ca7ba02b7923bca12992f9&",
    "Burletta": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236185084399676/Burletta_Blueprint.webp?ex=6953fdcf&is=6952ac4f&hm=b8d50829af757afbc25a127152ff707b250e55aca499593b108853648727ba79&",
    "Combat MK3 Aggressive": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236301069484247/Combat_MK3_Aggressive_Blueprint.webp?ex=6953fdeb&is=6952ac6b&hm=0755c108a2e3a5aa212e7e8d0e787ac1a574979feebe0ae0296bb6e4989a981c&",
    "Combat MK3 Flanking": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236301459558529/Combat_MK3_Flanking_Blueprint.webp?ex=6953fdeb&is=6952ac6b&hm=2ad8e37f96f77bb8e6bc80de537695a2ac2114521c99adf49e74a524b2d0e02a&",
    "Complex Gun Parts": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236302374174871/Complex_Gun_Parts_Blueprint.webp?ex=6953fdeb&is=6952ac6b&hm=1b959186d3f8967da2f22d43b852796cf110840bd1c0c10e06383b760050cae4&",
    "Compensator II": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236301791039713/Compensator_II_Blueprint.webp?ex=6953fdeb&is=6952ac6b&hm=084e2d59da9c281cab28c6e10edd292c7cb2de70b0809b8c795cc7662d69c82e&",
    "Compensator III": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236302097092730/Compensator_III_Blueprint.webp?ex=6953fdeb&is=6952ac6b&hm=d73c06b306b3ecf6315b18cd9e7e9da1c223e9d06855bb6a045248ca7ebd954b&",
    "Deadline Mine": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236302818644179/Deadline_Blueprint.webp?ex=6953fdeb&is=6952ac6b&hm=83db9a287778be0812af8b0685ee3b056372f11311dcb10fc477e0aa63e95bb4&",
    "Defibrillator": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236303221293191/Defibrillator_Blueprint.webp?ex=6953fdeb&is=6952ac6b&hm=194ab0c0bf474ca524290823226d613e8aa3c62fc622cb312738584ebfa4905d&",
    "Equalizer": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236303569424538/Equalizer_Blueprint.webp?ex=6953fdeb&is=6952ac6b&hm=db6ad93d38cfee30908099ff988a7834cc71ae319b2e957afcf04aeb0387106c&",
    "Explosive Mine": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236303955427389/Explosive_Mine_Blueprint.webp?ex=6953fdeb&is=6952ac6b&hm=8349c142b7b1c4d18f94c7c59e344f943304ebd989b6f8fd7668bf93c974c582&",
    "Extended Barrel": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236304286781440/Extended_Barrel_Blueprint.webp?ex=6953fdeb&is=6952ac6b&hm=517fbde61a1baf188204d15eed3da41f35738ba705c0eb0bcb6c4f9f488e62ce&",
    "Extended Light Mag II": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236385953812681/Extended_Light_Mag_II_Blueprint.webp?ex=6953fdff&is=6952ac7f&hm=9afb33b9fc9e05f129ef1e01eda5fb8696182bcae2c99e0e892a5df9b827dec1&",
    "Extended Light Mag III": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236386377568306/Extended_Light_Mag_III_Blueprint.webp?ex=6953fdff&is=6952ac7f&hm=4681d50abc4c35391c72dab16c9ae12605545960e733aa895b5f1eba619f8522&",
    "Extended Medium Mag II": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236386838810694/Extended_Medium_Mag_II_Blueprint.webp?ex=6953fdff&is=6952ac7f&hm=dfcb19395fdca6d7714f33219262177528c5de9e14429f1423740245c20a05a4&",
    "Extended Medium Mag III": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236387493253213/Extended_Medium_Mag_III_Blueprint.webp?ex=6953fdff&is=6952ac7f&hm=7673b4937d8cdd5dee7003089c40008999f1758e8923bba9d5ae48397ebc7baa&",
    "Extended Shotgun Mag II": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236387887513728/Extended_Medium_Shotgun_Mag_II_Blueprint.webp?ex=6953fdff&is=6952ac7f&hm=a1e2c3ae4c2f277662702ea3cfc6f1d1753ec33cf46482470981aa20bf51573c&",
    "Extended Shotgun Mag III": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236388403282142/Extended_Shotgun_Mag_III_Blueprint.webp?ex=6953fdff&is=6952ac7f&hm=75aa2392fa1cd57ba41f30e9558e35398aa6d0ed01f86c97eab401c88ac5da32&",
    "Fireworks Box": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236388868980817/Fireworks_Box_Blueprint.webp?ex=6953fe00&is=6952ac80&hm=e6e86ef0a12f3b83ecc7397152ddd3d8c3dc46b26beec18a30e0f7ce39ccb7b5&",
    "Gas Mine": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236389766430974/Gas_Mine_Blueprint.webp?ex=6953fe00&is=6952ac80&hm=09d719ec3bf8a0fce769d681280f7b63d6415a38a4e1633ca4001fb353112bec&",
    "Green Light Stick": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236390299238603/Green_Light_Stick_Blueprint.webp?ex=6953fe00&is=6952ac80&hm=056558a29b52e6ae597c416fcb56b42261a0c96f16872afd033e47a60e9fab07&",
    "Hullcracker": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236390609752236/Hullcracker_Blueprint.webp?ex=6953fe00&is=6952ac80&hm=5747e554dff6f185dc765c3a0a484bd5cd8a2e6b25d3b337827bcf421d317118&",
    "Il Toro": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236479096717394/IL_Toro_Blueprint.webp?ex=6953fe15&is=6952ac95&hm=538e671838f0d3e0d672518e58b297b8b1c0652f5949f70bfa04e658bba4498a&",
    "Jolt Mine": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236479373672448/Jolt_Mine_Blueprint.webp?ex=6953fe15&is=6952ac95&hm=a064fd48362a97d158d6f9a48801a52e4f69946e69d269630563bf12f11b71a5&",
    "Jupiter": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236479977525340/Jupiter_Blueprint.webp?ex=6953fe15&is=6952ac95&hm=c4bd1d1ef1d94a53c1bc57e97817feb87903b780c8d5eaa626501288658eec87&",
    "Light Gun Parts": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236480308871262/Light_Gun_Parts_Blueprint.webp?ex=6953fe15&is=6952ac95&hm=2bfec87ecff364342067aea86316a8a9d660b9f7c0d62ee0b2b8473ac187ce80&",
    "Lightweight Stock": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236480665518375/Lightweight_Stock_Blueprint.webp?ex=6953fe15&is=6952ac95&hm=101e1786d790688c1cec97f2bb85bd019968dcdc4759e47c4ff68ce8436a6f57&",
    "Looting MK3 Cautious": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236480958992592/Looting_MK3_Cautious_Blueprint.webp?ex=6953fe16&is=6952ac96&hm=be69b4428bb7c5f52f6f87c6fdac5c20ac9a1dc888fa905c9de88209d4a5bb2c&",
    "Looting MK3 Survivor": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236481286144070/Looting_MK3_Survivor_Blueprint.webp?ex=6953fe16&is=6952ac96&hm=92f3c993b20df25b01f912234ffbe706ed1bdcb1a815a64c71837d77b4e9ce0e&",
    "Lure Grenade": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236481621819626/Lure_Grenade_Blueprint.webp?ex=6953fe16&is=6952ac96&hm=b87e0b8c172e9d20cc9c712fd5c0073ae4055122fcf9671f7378d1cc8a5292ae&",
    "Medium Gun Parts": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236481928134747/Medium_Gun_Parts_Blueprint.webp?ex=6953fe16&is=6952ac96&hm=d31bc3913d68d1dd4e34378eb25f53bf0aefbeb84bfae26cb38225c603e99e9d&",
    "Muzzle Brake II": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236482267611136/Muzzle_Brake_II_Blueprint.webp?ex=6953fe16&is=6952ac96&hm=b2d9143d8e3d6a86db1f53827dd3758ae497f8c1d2cc9fa133126c322c9bc5c0&",
    "Muzzle Brake III": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236625951883410/Muzzle_Brake_III_Blueprint.webp?ex=6953fe38&is=6952acb8&hm=760f4fef000ab0d86cddf86a02d497af42d28f3cbf5feb9923a3dd902d65414d&",
    "Osprey": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236626983948391/Osprey_Blueprint.webp?ex=6953fe38&is=6952acb8&hm=77fac1a8141fe50918a1b27be7c1430fd1a69145733982084eeb1da7d191b498&",
    "Padded Stock": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236627520815156/Padded_Stock_Blueprint.webp?ex=6953fe38&is=6952acb8&hm=74d612aadc7fdb34bd7a856378e316f40c5c7a5cada7fd0a0cf0631f6bf1fe0c&",
    "Pulse Mine": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236628300693565/Pulse_Mine_Blueprint.webp?ex=6953fe39&is=6952acb9&hm=819ed77dc8e4823d675903cb0085846e2ba56b307677e66737a4557993bdd613&",
    "Red Light Stick": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236629718372372/Red_Light_Stick_Blueprint.webp?ex=6953fe39&is=6952acb9&hm=42037ff1bc6c50e9c797bd4cae922ce3ec45f375e6c6fcaa8a868c9216d36bf3&",
    "Remote Raider Flare": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236630301638676/Remote_Raider_Flare_Blueprint.webp?ex=6953fe39&is=6952acb9&hm=549ea537e823853ebbced47efd66293b5a43c5e091d5c26f332aac26833193f0&",
    "Seeker Grenade": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236630745972948/Seeker_Grenade_Blueprint.webp?ex=6953fe39&is=6952acb9&hm=b52b707f73e1d647d2ee3b7702d9bdb601163f31b16f6cb3b313c0e085649f29&",
    "Shotgun Choke II": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236631228584200/Shotgun_Choke_II_Blueprint.webp?ex=6953fe39&is=6952acb9&hm=d4b745fa6793cf6ce9990731d304c5df65ae3cdb7c6e3d1336e9b471067111d9&",
    "Shotgun Choke III": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236631828103361/Shotgun_Choke_III_Blueprint.webp?ex=6953fe3a&is=6952acba&hm=1811119178edd65eb7203623919302368e9eb4f4acd0e598f264c30f81bc8481&",
    "Shotgun Silencer": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236632536944877/Shotgun_Silencer_Blueprint.webp?ex=6953fe3a&is=6952acba&hm=012772b99e0b2f0f5b93548e6583bc3a5e8b39d707181bb364c5575be1f5078c&",
    "Showstopper": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236845528023202/Showstopper_Blueprint.webp?ex=6953fe6c&is=6952acec&hm=c11f89bf09fac1d8c044ec92e9a79e58548c3bb5f26af810f90138e0f2930bd4&",
    "Silencer I": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236846106706043/Silencer_I_Blueprint.webp?ex=6953fe6d&is=6952aced&hm=9de0ea585eab6278017520c1af01def06bee45b72ff79f04bb81557da05b9f39&",
    "Silencer II": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236846618542093/Silencer_II_Blueprint.webp?ex=6953fe6d&is=6952aced&hm=39dda1f7b6984a7916eafff284c5ff177ed826c1430c2dba405387f91fad0893&",
    "Smoke Grenade": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236847088308418/Smoke_Grenade_Blueprint.webp?ex=6953fe6d&is=6952aced&hm=7c393d4d1ba2de9625fe1fe1fcec04e2a20f14d0b61d5eef9f461fba51353274&",
    "Snap Hook": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236847474311209/Snap_Hook_Blueprint.webp?ex=6953fe6d&is=6952aced&hm=874aaef8c6b3907f1fecb2137c63b056091200dcd15e637ea3d467b43c8a8158&",
    "Stable Stock II": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236848107524323/Stable_Stock_II_Blueprint.webp?ex=6953fe6d&is=6952aced&hm=34cac6103294c998898603d98af691ae7504377bd873af55a6ff69a62a3e2c2b&",
    "Stable Stock III": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236848749121763/Stable_Stock_III_Blueprint.webp?ex=6953fe6d&is=6952aced&hm=5c0bbda36437abf4064020908e3c57112a8eafc4f26653069b197b991769be36&",
    "Tactical MK3 Defensive": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236849122672690/Tactical_Mk3_Defensive_Blueprint.webp?ex=6953fe6d&is=6952aced&hm=09c5822356d5e5fa7f9a382ae26fc8ea97bfa03115fe30149f5243c0757d91ed&",
    "Tactical MK3 Healing": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236849583788145/Tactical_MK3_Healing_Blueprint.webp?ex=6953fe6d&is=6952aced&hm=dade066aa318ff9cbe98dba100360ca80e518ede8783de85b88f5fc6a8cf829b&",
    "Tagging Grenade": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236850112401600/Tagging_Grenade_Blueprint.webp?ex=6953fe6e&is=6952acee&hm=5e68dc6717b654982cda467dc950161d920106811181713019a7adae3b31be2c&",
    "Tempest": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236944345698334/Tempest_Blueprint.webp?ex=6953fe84&is=6952ad04&hm=1afc9a30d7d18c6dacdcc3eeca76be4ce786719f97de50f76c7de56ddac96b85&",
    "Torrente": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236944647815240/Torrente_Blueprint.webp?ex=6953fe84&is=6952ad04&hm=984e4d4060c8db3ff7a0ca05159bf1b2dba7b07dd581ddd686a801f487cd46d8&",
    "Trailblazer Grenade": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236945331617884/Trailblazer_Grenade_Blueprint.webp?ex=6953fe84&is=6952ad04&hm=2e02d6980d4a76451d2ec7b112f53c6a56994414794ded4b199514d8d0fde340&",
    "Trigger Nade": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236945864036577/Trigger_Nade_Blueprint.webp?ex=6953fe84&is=6952ad04&hm=06d92dbd48592672ff8966ab7f15f0aed1d687580f06901304ed8e8b42e41f10&",
    "Venator": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236946409422878/Venator_Blueprint.webp?ex=6953fe85&is=6952ad05&hm=b78af9ed37e27afd558ed608e43ccbe460c459e67a8a7ed56ac1e5d4c1fe9fc5&",
    "Vertical Grip II": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236946787045509/Vertical_Grip_II_Blueprint.webp?ex=6953fe85&is=6952ad05&hm=95cb084836e3d4286053605cfda87018aa7c2ea34a20ebba5ff7aa6a0fa7a653&",
    "Vertical Grip III": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236947147489280/Vertrical_Grip_III_Blueprint.webp?ex=6953fe85&is=6952ad05&hm=14fd32acd0e5aac4b1dacbd69e6e026bed3e53909027383158676d65ee2d39aa&",
    "Vita Shot": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236947508334602/Vita_Shot_Blueprint.webp?ex=6953fe85&is=6952ad05&hm=181b7e480d52f12536d6cc181382862cdbd31124899fbb883ebea2f37c41427c&",
    "Vita Spray": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236947927896218/Vita_Spray_Blueprint.webp?ex=6953fe85&is=6952ad05&hm=9ef5300783bb317cb9128e2675413841212686b0cb36e5d8fec0e71b96783c09&",
    "Vulcano": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236948347064381/Vulcano_Blueprint.webp?ex=6953fe85&is=6952ad05&hm=2fb4befb0bc2b6fab4a288e775c91f56a294e8e8aae53c0016f9ba6cefc4d785&",
    "Wolfpack": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236990927634494/Wolfpack_Blueprint.webp?ex=6953fe8f&is=6952ad0f&hm=d1e765b2a7365891891c4fd05dffe87cc966d1fb8c3dc23c5dc190a1dfc4c187&",
    "Yellow Light Stick": "https://cdn.discordapp.com/attachments/1455235633143480445/1455236991309451295/Yellow_Light_Stick_Blueprint.webp?ex=6953fe8f&is=6952ad0f&hm=7496e06786130fb08e56f7893c869b51a47650264cbfd69a4249f08e7f1bbf81&",
}

# Sort keys alphabetically for dropdown
BLUEPRINT_NAMES_SORTED: List[str] = sorted(BLUEPRINT_CATALOG.keys())


# ------------- DATABASE -------------

mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DB_NAME]
blueprints_col = db[COLLECTION_NAME]


# ------------- DISCORD BOT SETUP -------------

class BlueprintDropdown(discord.ui.Select):
    def __init__(self, user_id: int):
        options = [
            discord.SelectOption(label=name, value=name)
            for name in BLUEPRINT_NAMES_SORTED
        ]
        super().__init__(
            placeholder="Select a blueprint to add...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        selected_name = self.values[0]
        thumbnail_url = BLUEPRINT_CATALOG[selected_name]

        doc = {
            "name": selected_name,
            "thumbnail_url": thumbnail_url,
            "owner_id": interaction.user.id,
        }
        blueprints_col.insert_one(doc)

        await interaction.response.edit_message(
            content=f"Added **{selected_name}** to your extras.",
            view=None
        )


class BlueprintDropdownView(discord.ui.View):
    def __init__(self, user_id: int, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.add_item(BlueprintDropdown(user_id))


class BlueprintBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,   # <-- FIXED: use the correct intents object
            application_id=None
        )

    async def setup_hook(self):
        await self.tree.sync()


bot = BlueprintBot()


# ------------- SLASH COMMANDS -------------

@bot.tree.command(name="add_blueprint", description="Add one of your extra blueprints to the marketplace.")
async def add_blueprint(interaction: discord.Interaction):
    view = BlueprintDropdownView(interaction.user.id)
    await interaction.response.send_message(
        "Select the blueprint you want to add:",
        view=view,
        ephemeral=True
    )


@bot.tree.command(name="market", description="View all blueprints currently listed by everyone.")
async def market(interaction: discord.Interaction):
    docs = list(blueprints_col.find({}))

    if not docs:
        await interaction.response.send_message("No blueprints have been listed yet.", ephemeral=True)
        return

    embeds: List[discord.Embed] = []
    for doc in docs:
        name = doc.get("name", "Unknown")
        thumbnail_url = doc.get("thumbnail_url")
        owner_id = doc.get("owner_id")
        owner_mention = f"<@{owner_id}>" if owner_id else "Unknown"

        embed = discord.Embed(
            title=name,
            description=f"Owner: {owner_mention}",
            color=discord.Color.blue()
        )
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        embeds.append(embed)

    # Discord allows up to 10 embeds per message
    chunks = [embeds[i:i + 10] for i in range(0, len(embeds), 10)]

    await interaction.response.send_message(embeds=chunks[0])
    for chunk in chunks[1:]:
        await interaction.followup.send(embeds=chunk)


@bot.tree.command(name="my_blueprints", description="View the blueprints you have listed.")
async def my_blueprints(interaction: discord.Interaction):
    docs = list(blueprints_col.find({"owner_id": interaction.user.id}))

    if not docs:
        await interaction.response.send_message("You haven't listed any blueprints yet.", ephemeral=True)
        return

    embeds: List[discord.Embed] = []
    for doc in docs:
        name = doc.get("name", "Unknown")
        thumbnail_url = doc.get("thumbnail_url")

        embed = discord.Embed(
            title=name,
            description=f"Owner: {interaction.user.mention}",
            color=discord.Color.green()
        )
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        embeds.append(embed)

    chunks = [embeds[i:i + 10] for i in range(0, len(embeds), 10)]

    await interaction.response.send_message(embeds=chunks[0], ephemeral=True)
    for chunk in chunks[1:]:
        await interaction.followup.send(embeds=chunk, ephemeral=True)


@bot.tree.command(name="remove_blueprint", description="Remove one of your listed blueprints.")
async def remove_blueprint(interaction: discord.Interaction):
    docs = list(blueprints_col.find({"owner_id": interaction.user.id}))

    if not docs:
        await interaction.response.send_message("You don't have any blueprints listed.", ephemeral=True)
        return

    # Build a simple numbered list for the user to pick from
    description_lines = []
    for idx, doc in enumerate(docs, start=1):
        description_lines.append(f"{idx}. {doc.get('name', 'Unknown')}")

    embed = discord.Embed(
        title="Your listed blueprints",
        description="\n".join(description_lines),
        color=discord.Color.orange()
    )
    embed.set_footer(text="Reply with the number of the blueprint you want to remove.")

    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check(m: discord.Message):
        return (
            m.author.id == interaction.user.id
            and m.channel.id == interaction.channel_id
        )

    try:
        msg = await bot.wait_for("message", check=check, timeout=60.0)
        index = int(msg.content.strip())
        if index < 1 or index > len(docs):
            await interaction.followup.send("Invalid number. No blueprint removed.", ephemeral=True)
            return

        to_remove = docs[index - 1]
        blueprints_col.delete_one({"_id": to_remove["_id"]})
        await interaction.followup.send(f"Removed **{to_remove.get('name', 'Unknown')}** from your listings.", ephemeral=True)

    except asyncio.TimeoutError:
        await interaction.followup.send("Timed out waiting for a response. No blueprint removed.", ephemeral=True)
    except ValueError:
        await interaction.followup.send("Please reply with a valid number next time.", ephemeral=True)


# ------------- RUN -------------

if __name__ == "__main__":
    if not DISCORD_TOKEN or not MONGODB_URI:
        print("Please set DISCORD_TOKEN and MONGODB_URI environment variables.")
    else:
        bot.run(DISCORD_TOKEN)
