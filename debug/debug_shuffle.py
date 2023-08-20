import random

sample_promtps = [
    "an illustrated person in a hooded green dress standing with a skateboard and a bloody knife, 1girl, bandaid on leg, solo, hood, choker, shoes, bandaid, yellow eyes, blood, hood up, sneakers, hoodie, long hair, grey background, bandaid on knee, grey hair, black choker, hand in pocket, white footwear, holding, standing, closed mouth, full body, weapon, sleeves past wrists, holding weapon, simple background",
    "there is a digital illustration depicting an elf-femme holding hand of a human male, 1girl, 1boy, dress, breasts, virtual youtuber, purple eyes, pointy ears, animal ears, cleavage, smile, black hair, long hair, gloves, choker, cape, white dress, chandelier",
    "an anime character hugging another anime character that is wearing angel wings above their head, multiple boys, 2boys, male focus, red hair, halo, horns, white hair, wings, demon horns, shirt, yaoi, jacket, short hair, looking at another, virtual youtuber, black background, jewelry, white shirt, necktie, long sleeves, earrings, angel and devil",
    "a man with backpack near door of a small storefront on side of street, bicycle, ground vehicle, scenery, outdoors, plant, solo, potted plant, 1girl, shirt, black shirt, building, sign, wide shot, signature, road, street, standing, alley, short hair",
    "the anime style illustration of a girl with white hair laying on floor surrounded by many colorful pieces, 1girl, solo, yellow eyes, very long hair, ogasawara hisame, twintails, black thighhighs, aiamu_iamu, heaven burns red, ribbon, white hair, horns, holding, handgun, looking at viewer, knife, wide sleeves, bangs, long sleeves, weapon, white skirt, gun, absurdres, highres",
    "this is an anime styled picture of a young girl playing with cards in the air, safe, 1girl, solo, brown hair, hair bow, detached sleeves, hair tubes, red bow, smile, red skirt, gohei, wide sleeves, hakurei reimu, long hair, ofuda, ribbon trim, ribbon-trimmed sleeves, frills, yuujin_(yuzinn333), looking at viewer, holding, sun, white socks, touhou, socks, brown eyes, closed mouth, cloud, sarashi, bangs, blue sky, bare shoulders, hair between eyes, frilled skirt, blush, day, nontraditional miko, red vest, outdoors, white sleeves, red shirt, long sleeves, yellow eyes, vest, flying, feet out of frame, between fingers, medium hair, hand up, arm up, absurdres, highres",
    "a anime girl wearing sneakers and pants sitting near a wall painted with graffiti writing, safe, 1girl, solo, graffiti, virtual youtuber, long hair, spray can, thick eyebrows, shoes, hxxg, long sleeves, white skirt, open jacket, looking at viewer, hololive, blue jacket, usada pekora (4th costume), knee up, animal ears, blush, usada pekora, rabbit ears, road, hair over shoulder, fur trim, open clothes, white shirt, looking away, white footwear, fur-trimmed jacket, blue necktie, tied ears, bangs, street, hair ribbon, hair bun, closed mouth, kneeling, ribbon, sneakers, carrot hair ornament, food-themed hair ornament, hairpin, short eyebrows, neckerchief, one knee, hair between eyes, pleated skirt, off shoulder, yellow eyes, wall, white sailor collar, rabbit girl, white socks, sitting, blood, outdoors, light blue hair, collarbone, blue choker, absurdres, highres",
    "two anime characters are standing in some sort of hall with two girls behind them, safe, multiple girls, red eyes, black dress, red hair, pointy ears, white hair, 3girls, official alternate costume, warfarin (arknights), mudrock (obsidian) (arknights), arknights, demon horns, vigna (arknights), mudrock (arknights), smile, miike_(992058), sleeveless dress, black headwear, crown braid, jewelry, dated, bare shoulders, open mouth, looking back, cup, curtains, thighs, drinking glass, detached sleeves, black choker, pelvic curtain, necklace, earrings, very long hair, arm tattoo, short sleeves, albino, sleeveless, thigh strap, cleavage, :d, bangs, hat, indoors, parted lips, ahoge, leaning forward, medium breasts, alternate costume, bracelet, english text, bottle, window, highres",
    "In the center of a vast flower field, BREAK the Gomphrena globosa (Globe Amaranth) blooms beautifully, its purple petals shimmering vividly under the sun. BREAK Nearby, a girl dressed in a Chinese dress stands, gently holding the flower. A dreamy expression fills her eyes, evoking the flower's meanings of \"Unchanging love\", \"Eternal love\", and \"Immortality\". BREAK The surrounding breeze tenderly rustles her dress and the flowers., 1girl, flower, dress, solo, outdoors, white dress, holding, holding flower, short sleeves, profile, closed eyes, field, purple flower, blurry, from side",
]


def clean_limited_shuffle_dropout_processor(prompt: str) -> (str, bool):
    """
    cleaning:
        - remove tags that are subsets of other tags
        - remove noisy symbols and urls from human inputs

    limited shuffling:
        - shuffle tags in the prompt, excluding the starting sentence
        - shuffle begins at the first <SHUFFLE_START_OFFSET>th tag
        - shuffles with a limited shuffle distance of <MAX_SHUFFLE_OFFSET>

    random dropout:
        - dropout images with synthetic tags <SYNTHETIC_MARKER> with a probability of <SYNTHETIC_DROPOUT_RATE>

    :param prompt: raw prompt
    :return: (prompt:str, skip_image:bool)
    """
    SEPARATOR = ","  # separator between tags
    IS_SENTENCE_THRES = 4  # minimum space-separated parts of the starting prompt to be seen as sentence
    SHUFFLE_START_OFFSET = 2  # start shuffling at first-n <separator> separated part
    MAX_SHUFFLE_OFFSET = 4  # maximum distance of shuffle from the original position
    SYNTHETIC_MARKER = "<|generated|>"  # marker for synthetic images
    SYNTHETIC_DROPOUT_RATE = 0.6  # probability of dropping synthetic images

    import re

    def _find_subset_tags(tags_list: list) -> set:
        subset_tags = set()
        for i, tag1 in enumerate(tags_list):
            for j, tag2 in enumerate(tags_list):
                if i != j and tag1.strip() in tag2:
                    subset_tags.add(tag1)
                    break
        return subset_tags

    def _limited_shuffle(tags: list[str], max_offset: int) -> list[str]:
        shuffled_tags = tags.copy()
        n = len(tags)
        swapped_indices = set()  # swapped indices

        for i in range(n):
            if i in swapped_indices:  # swapped already
                continue

            # set the left and right bound of the offset
            left_bound = max(i - max_offset, 0)
            right_bound = min(i + max_offset, n - 1)

            # Select a random index within the offset range
            swap_index = random.randint(left_bound, right_bound)

            # Not swapping with itself and not swapping with an already swapped index
            if swap_index != i and swap_index not in swapped_indices:
                # Randomly swaps the tags & mark the indexes as swapped
                shuffled_tags[i], shuffled_tags[swap_index] = shuffled_tags[swap_index], shuffled_tags[i]
                swapped_indices.add(i)
                swapped_indices.add(swap_index)

        return shuffled_tags

    if not prompt:
        return prompt, False

    # Marker exists and is not a empty string
    if SYNTHETIC_MARKER and SYNTHETIC_MARKER in prompt:
        if random.random() < SYNTHETIC_DROPOUT_RATE:
            return prompt, True

    fixed_prompt = prompt.replace(SYNTHETIC_MARKER, "").strip()

    # Remove url
    fixed_prompt = re.sub(r"<http\S+>", "", fixed_prompt).strip()

    # Remove common webui tags
    STRIP_KEYS = ("BREAK", "&", "$", "#", "**", "((", "))", "\\", "\"")
    for key in STRIP_KEYS:
        fixed_prompt = fixed_prompt.replace(key, "")

    # Fix common punctuations
    REPLACEMENT_MAP = [("\n", ", "), (" ,", ","), (" .", "."), (" :", ":"), (" ;", ";"), ("  ", " "), ("、", ","),
                       ("|", ","), ]

    for _from, _to in iter(REPLACEMENT_MAP):
        fixed_prompt = fixed_prompt.replace(_from, _to)

    # Remove double spaces
    fixed_prompt = re.sub(r"\s+", " ", fixed_prompt).strip()

    # Splitting prompt by separator
    parts = fixed_prompt.split(SEPARATOR)
    parts = [part.strip() for part in parts]

    # Finding the index of the first non-sentence
    sentence_index = next((i for i, part in enumerate(parts) if len(part.split()) <= IS_SENTENCE_THRES), len(parts))

    # Keep the first <sentence_index> parts as it is
    preserved, to_shuffle = parts[:sentence_index], parts[sentence_index:]

    subset_tags = _find_subset_tags(to_shuffle)
    tags_to_keep = [tag for tag in to_shuffle if tag not in subset_tags]

    # Shuffling the remaining tags
    kept_tags = tags_to_keep[:SHUFFLE_START_OFFSET]
    shuffled_tags = _limited_shuffle(tags_to_keep[SHUFFLE_START_OFFSET:], max_offset=MAX_SHUFFLE_OFFSET)
    out = ", ".join(preserved + kept_tags + shuffled_tags)

    return out, False


from tqdm import tqdm


def test_drive():
    nj_prompt = "In the center of a vast flower field, BREAK the Gomphrena globosa (Globe Amaranth) blooms beautifully, its purple petals shimmering vividly under the sun. BREAK Nearby, a girl dressed in a Chinese dress stands, gently holding the flower. A dreamy expression fills her eyes, evoking the flower's meanings of \"Unchanging love\", \"Eternal love\", and \"Immortality\". BREAK The surrounding breeze tenderly rustles her dress and the flowers., 1girl, flower, dress, solo, outdoors, white dress, holding, holding flower, short sleeves, profile, closed eyes, field, purple flower, blurry, from side"
    nj_prompt2 = "<https:s.mj.run/e0EGIpmjo14> Anime poster of girl, Amateur girl, shiny eyes, precious lips, chest and belly, semirealistic style. + Zoom portrait, apocalyptic, realistic, Cinematic, Color Grading, portrait Photography, Ultra - Wide Angle, Depth of Field, hyper - detailed, beautifully color - coded, insane details, intricate details, beautifully color graded, Unreal Engine, Cinematic, Color Grading, Editorial Photography, Photography, Photoshoot, Shot on 70mm lens, Depth of Field, DOF, Tilt Blur, Shutter Speed 1/ 1000, F/ 22, White Balance, 32k, Super - Resolution, Megapixel, Pro Photo RGB, VR, Lonely, Good, Massive, Half rear Lighting, Backlight, Natural Lighting, Incandescent, Optical Fiber, Moody Lighting, Cinematic Lighting, Studio Lighting, Soft Lighting, Volumetric, Conte - Jour, Beautiful Lighting, Accent Lighting, Global Illumination, Screen Space Global Illumination, Ray Tracing Global Illumination, Optics, Scattering, Glowing, Shadows, Rough, Shimmering, Ray Tracing Reflections, Lumen Reflections, Screen Space Reflections, Diffraction Grading, Chromatic Aberration, GB Displacement, Scan Lines, Ray Traced, Ray Tracing Ambient Occlusion, Anti - Aliasing, FKAA, TXAA, RTX, SSAO, Shaders, OpenGL - Shaders, GLSL - Shaders, Post Processing, Post - Production, Cell Shading, Tone Mapping, CGI, VFX, SFX, insanely detailed and intricate, hyper maximalist, elegant, hyper realistic, super detailed, dynamic pose, photography, Hyper realistic, volumetric, photorealistic, ultra photoreal, ultra - detailed, intricate details, 8K, super detailed, full color, ambient occlusion, sherif, pixelart, volumetric lighting, high contrast, HDR., 1girl, solo, cyborg, mechanical arms, looking at viewer, breasts, black hair, white hair, letterboxed, multicolored hair, parted lips, bangs, cyberpunk, robot joints, bodysuit, white background, lips, blunt bangs, science fiction, medium breasts, joints"
    test_subset_rm = "<|generated|> a long sentence with more than 4, 1 girl, girl, another sentence, a tall girl, A, B, C, D, E, F, G, one, two, three"

    real_prompt_marked = "広大な花畑の中心に、千日紅（Gomphrena globosa）の花か美しく咲いている.その紫の花ひらか太陽の下て鮮やかに光る.近くには、チャイナトレスを纏った少女か立ち、その花を優しく手に取っている.彼女の瞳には夢見るような表情か浮かひ、千日紅の花言葉\"変わらぬ恋\"\"永遠の恋\"\"不死\"を思い起こさせる.周囲の風か、彼女の髪と花をやさしくなひかせている., 1girl, flower, solo, hair bun, single hair bun, outdoors, holding flower, blurry, necklace, chinese clothes, black hair, field, jewelry, dress, looking down, from side, day, blurry background, holding <|generated|>"

    for prompt in tqdm([nj_prompt, nj_prompt2, test_subset_rm] + sample_promtps * 10000):
        new_prompt, train_dropout = clean_limited_shuffle_dropout_processor(real_prompt_marked)

        print(prompt)

    print("D")


if __name__ == '__main__':
    test_drive()
